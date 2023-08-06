import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='d3cloud',
    version='0.7.1',
    author='Tomas Ruiz',
    author_email='tomasruiz@d3atech.com',
    description='D3Cloud API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://d3design.tools',
    project_urls={
        "Bug Tracker": "https://github.com/"
    },
    license='MIT',
    packages=['d3cloud'],
    install_requires=['requests']
)