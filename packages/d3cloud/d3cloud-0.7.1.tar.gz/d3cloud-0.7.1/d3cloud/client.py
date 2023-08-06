from __future__ import print_function, division, absolute_import
import ssl, traceback, sys, json, os, requests, shutil, time

if sys.version_info[0] > 2: 
    import urllib.request as urllib2
    from urllib.parse import urlencode
else:
    import urllib2
    from urllib import urlencode

from datetime import datetime

__version__ = '0.7.1'
URL = 'https://d3design.tools/d3cloud'


class Client(object):
    """Base client object to interact with D3 Cloud.

        Args:
            user (str): Username.
            apiToken (str): API token.
    """
    def __init__(self,user,apiToken):
        self._user = user
        self._apiToken = apiToken
        # Check credentials and initialize user.
        response = self.__post(URL+'/api_initialize',{'version':__version__})
        if response['valid']:
            print('INFO [client]: Connected to D3 Cloud.')
        if not response['valid']:
            print(response['info'])

    # Private.

    def __post(self,url,data={},returnRaw=False):
        """Send POST requests to server.

        Args:
            url (str): Endpoint to end request to.
            data (dict, optional): Data to be sent in POST request. Defaults to {}.

        Returns:
            dict: Body of POST request response.
        """
        data['user'] = self._user
        data['apiToken'] = self._apiToken
        dataList = []
        for key in data:
            dataList.append((key,data[key]))
        post = urlencode(dataList).encode("utf-8")
        req = urllib2.Request(url, data=post)
        context = ssl._create_unverified_context() # ? Passing this ssl context is an unsafe hack and should be done properly by checking certs.
        try:
            response = urllib2.urlopen(req, context=context)
            if returnRaw:
                return {'valid':True,'content':response.read()}
            else:
                return json.loads(response.read())
        except urllib2.HTTPError as err:
            if err.code == 502:
                print('ERROR [client]: Could not reach D3 Cloud, please try again later and contact support if the problem persists.')
                return {'valid':False, 'info':'Could not reach D3 Cloud, please try again later and contact support if the problem persists.'}
            else:
                traceback.print_exc()
                print('ERROR [client]: Something went wrong, please contact support.')
                return {'valid':False, 'info':'Something went wrong, please contact support.'}

    def __downloadResults(self,projectName,simulationName,resultsType,localPath,cases=None):
        """Download simulation results.

        Args:
            projectName (str): Name of project the simulation belongs to.
            simulationName (str): Name of simulation to get results from.
            resultsType (str): Extension of results to download from: csv, pdf, png, sce and ply.
            localPath (str): Local path to download all results as zip.
            cases (list[float], optional): List of cases ID to download results for. Set to None for downloading all available cases. Defaults to None.
        """
        if self.simulationState(projectName,simulationName) != 'finished':
            print('WARNING [client]: Simulation must be on "finished" state to download its results.')
            return
        response = self.__post(URL+'/api_valid_results_size_limit',{'projectName':projectName,'simulationName':simulationName,'extension':'csv','cases':cases})
        if response['valid']:
            if not response['validSize']:
                print('ERROR [client]: Requested results exceed download size limit, please select fewer cases.')
                return
            response = self.__post(URL+'/api_downloadResults',{'projectName':projectName,'simulationName':simulationName,'cases':cases,'resultsType':resultsType}, returnRaw=True)
            if response['valid']:
                with open(localPath,'wb') as f:
                    f.write(response['content'])
            else:
                print('ERROR [client]: Failed to download results.')
        else:
            print('ERROR [client]: Failed to download results.')

    # Public.

    def newProject(self,projectName):
        """Create new project (if project does not exists).
        
        Args:
            projectName (str): Name given to new project.
        
        Returns:
            boolean: Wether new project creation request was successful or not.
        """
        response = self.__post(URL+'/api_newProject',{'projectName':projectName})
        print('INFO [client|newProject]:',response['info'])
        return response['valid']

    def deleteProject(self,projectName):
        """Delete project.

        Args:
            projectName (str): Name of project to delete.
        
        Returns:
            boolean: Wether project deletion was successful or not.
        """
        response = self.__post(URL+'/api_deleteProject',{'projectName':projectName})
        print('INFO [client|deleteProject]:',response['info'])
        return response['valid']

    def projectsInfo(self):
        """Retrieve information for all user's projects.
        
        Returns:
            dict: Dictionary matching each project name with a list of its simulations information (type, points, state, description, etc).
        """
        info = self.__post(URL+'/api_projectsInfo')
        return info.get('projectsSimulationInfo',{})

    def newSimulation(self,projectName,simulationName,simulationType,simulationGeometries,simulationMatrix,simulationSettings):
        """Submit new simulation.

        Args:
            projectName (str): Name of project to create simulation in. If project does not exist the function will exit.
            simulationName (str): Name given to simulation. If the simulation already exists, the function will exit.
            simulationType (str): Simulation type (e.g. Sail Wind Tunnel). Please check the documentaiton for a full list
                                    of simulation types and their usage guides.
            simulationGeometries (str): Path to .zip containing all the geometries to be simulated. This .zip file must
                                        conform to the standard folder structure required by the D3Cloud. Please see the 
                                        documentation for more details on this.
            simulationMatrix (str): Path to .csv specifying all the conditions to be simulated. Please see the documentation
                                    for more details on the required fields for each simulation type.
            simulationSettings (str): Path to .json file specifying all simulation settings. Please see the documentation
                                        for more details on the settings required by each simulation type.
        Return:
            boolean: Wether simulation was submitted successfully or not.
        """
        # Check files exist.
        if not os.path.exists(simulationGeometries):
            print('WARNING [client|newSimulation]: Could not find geometries:',simulationGeometries)
            return False
        if not os.path.exists(simulationMatrix):
            print('WARNING [client|newSimulation]: Could not find matrix:',simulationMatrix)
            return False
        if not os.path.exists(simulationSettings):
            print('WARNING [client|newSimulation]: Could not find settings:',simulationSettings)
            return False
        
        # Check simulation settings json has no syntax errors.
        try:
            json.load(open(simulationSettings,'r'))
        except:
            print('WARNING [client|newSimulation]: Simulation settings file is not valid JSON.')
            return False

        # Check that project exists.
        if projectName not in self.projectsInfo():
            print('WARNING [client|newSimulation]: Project',projectName,'does not exist. Please create it first with client.newProject().')
            return False

        # Check that simulation does not exists already.
        if simulationName in [simulation['name'] for simulation in self.projectsInfo()[projectName]]:
            print('WARNING [client|newSimulation]: Simulation',simulationName,'does exist already. Please delete it or create one with a different name.')
            return False

        # Upload .zip file with geometries.
        print('INFO [client|newSimulation]: Uploading geometries...')
        if os.path.splitext(simulationGeometries)[1] != '.zip':
            print('WARNING [client|newSimulation]: Please zip geometries.')
            return False

        with open(simulationGeometries, 'rb') as f:
            r = requests.post(
                URL+'/upload',
                files = {'file1': f},
                data = {
                    'simulationType':simulationType,
                    'api':'true',
                    'username':self._user,
                    'apiToken':self._apiToken,
                    'projectName':projectName,
                    'caseName':simulationName
                },
                verify=False # ! TODO Quick unsafe hack until certs are served.
            )
            if r.status_code == 200:
                response = r.json()
                if response['valid']:
                    print('INFO [client|newSimulation]: Geometries uploaded successfully.')
                else:
                    print('ERROR [client|newSimulation]: Something went wrong uploading geometries:')
                    print(response['info'])
                    return False
            else:
                print('ERROR [client|newSimulation]: Server error '+str(r.status_code)+' during geometry upload. Please try again and if the problem persists contact support.')
                return False

        # Wait until (non-blocking) geometry upload finishes.
        status = 'waiting'
        while status in ['waiting','processing']:
            response = self.__post(
                URL+'/api_processGeometriesInfo',
                {
                    'projectName':projectName,
                    'simulationName':simulationName
                }
            )
            status = response['status']
            message = response['message']
            print('INFO [client|newSimulation]:',message)
            time.sleep(3)

        if status != 'finished':
            print('ERROR [client|newSimulation]: '+message)
            return False

        # Send request with matrix and simulation settings.
        with open(simulationMatrix,'r') as f:
            simulationMatrix = f.read()

        with open(simulationSettings,'r') as f:
            simulationSettings = f.read()

        response = self.__post(
            URL+'/api_newSimulation',
            {
                'simulationType':simulationType,
                'projectName':projectName,
                'simulationName':simulationName,
                'matrix':simulationMatrix,
                'settings':simulationSettings
            }
        )

        print('INFO [client|newSimulation]: '+response['info'])
        return response['valid']

    def deleteSimulation(self,projectName,simulationName):
        """Delete simulation.
        
        Args:
            projectName (str): Name of project the simulation belongs to.
            simulationName (str): Name of simulation to be deleted.
        
        Return:
            boolean: Wether simulation deletion was successful or not.
        """
        response = self.__post(URL+'/api_deleteSimulation',{'projectName':projectName,'simulationName':simulationName})
        print('INFO [client|deleteSimulation]:',response['info'])
        return response['valid']

    def simulationState(self,projectName,simulationName):
        """Retrieve state of a simulation. Possible states:
            - delete: Simulation has been registered for deletion.
            - stopping: Simulation has been registered for stopping.
            - waiting: Simulation is waiting to be processed.
            - queued: Simulation has been processed and sent to the queue.
            - running: Simulation is running in the cluster.
            - finished: Simulation has finished running and there are results files available.
            - failed: Simulation has finished running but there are no results files available.
            - skip: Simulation folder is being created and should not be procesed yet.
        
        Args:
            projectName (str): Name of project the simulation belongs to.
            simulationName (str): Name of simulation to get state from.
        
        Return:
            str/None: Simulation state or None if request failed.
        """
        projectInfo = self.projectsInfo().get(projectName,[])
        for simulation in projectInfo:
            if simulation['name'] == simulationName:
                return simulation['state']
        return None

    def downloadTable(self,projectName,simulationName):
        """Retrieve csv results table of a simulation.

        Args:
            projectName (str): Name of project the simulation belongs to.
            simulationName (str): Name of simulation to get results from.
        Return:
            str/None: Simulation results as a raw string or None if request failed.
        """
        if self.simulationState(projectName,simulationName) != 'finished':
            print('WARNING [client|downloadTable]: Simulation must be on "finished" state to download its results.')
            return
        response = self.__post(URL+'/api_downloadTable',{'projectName':projectName,'simulationName':simulationName})
        if response['valid']:
            return response['results']
        else:
            print('INFO [client|downloadTable]:',response['info'])

    def downloadCsv(self,projectName,simulationName,localPath,cases=None):
        """Download csv results of a simulation.

        Args:
            projectName (str): Name of project the simulation belongs to.
            simulationName (str): Name of simulation to get results from.
            localPath (str): Local path to download all results as zip.
            cases (list[float], optional): List of cases ID to download csv files for. Set to None for downloading all available cases. Defaults to None.
        """
        self.__downloadResults(projectName,simulationName,'csv',localPath,cases)

    def downloadReport(self,projectName,simulationName,localPath,cases=None):
        """Download auto-generated report of a simulation.

        Args:
            projectName (str): Name of project the simulation belongs to.
            simulationName (str): Name of simulation to get results from.
            localPath (str): Local path to download all results as zip.
            cases (list[float], optional): List of cases ID to download reports for. Set to None for downloading all available cases. Defaults to None.
        """
        self.__downloadResults(projectName,simulationName,'pdf',localPath,cases)

    def downloadImages(self,projectName,simulationName,localPath,cases=None):
        """Download image results of a simulation.

        Args:
            projectName (str): Name of project the simulation belongs to.
            simulationName (str): Name of simulation to get results from.
            localPath (str): Local path to download all results as zip.
            cases (list[float], optional): List of cases ID to download images for. Set to None for downloading all available cases. Defaults to None.
        """
        self.__downloadResults(projectName,simulationName,'png',localPath,cases)

    def downloadScenes(self,projectName,simulationName,localPath,cases=None):
        """Download Star-View+ scene files of a simulation.

        Args:
            projectName (str): Name of project the simulation belongs to.
            simulationName (str): Name of simulation to get results from.
            localPath (str): Local path to download all results as zip.
            cases (list[float], optional): List of cases ID to download scenes for. Set to None for downloading all available cases. Defaults to None.
        """
        self.__downloadResults(projectName,simulationName,'sce',localPath,cases)

    def downloadPly(self,projectName,simulationName,localPath,cases=None):
        """Download 3D view ply files of a simulation.

        Args:
            projectName (str): Name of project the simulation belongs to.
            simulationName (str): Name of simulation to get results from.
            localPath (str): Local path to download all results as zip.
            cases (list[float], optional): List of cases ID to download ply files for. Set to None for downloading all available cases. Defaults to None.
        """
        self.__downloadResults(projectName,simulationName,'ply',localPath,cases)
    
    def downloadEnsight(self,projectName,simulationName,localPath,cases=None):
        """Download ensight file of a simulation.

        Args:
            projectName (str): Name of project the simulation belongs to.
            simulationName (str): Name of simulation to get results from.
            localPath (str): Local path to download all results as zip.
            cases (list[float], optional): List of cases ID to download ensight file for. Set to None for downloading all available cases. Defaults to None.
        """
        self.__downloadResults(projectName,simulationName,'ensight',localPath,cases)