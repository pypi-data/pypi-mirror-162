# Model Definitions for Splunk IT Service Intelligence

## Setup Virtualenv

```
python3 -m venv /path/to/new/virtual/environment

source /path/to/new/virtual/environment/bin/activate
```

## Install the Python package

```
pip install --upgrade itsimodels
```

# Build the itsimodels distribution archive and upload it to PyPi
For releasing the packages you must have Maintainer access on PyPi 

There are two ways:
- [Build and release itsimodels packages manually](#build-and-release-itsimodels-packages-manually)
- [Build and release itsimodels packages automatically](#build-and-release-itsimodels-packages-automatically)
## Build and release itsimodels packages manually

Install the build dependencies:
```
pip install --upgrade setuptools wheel
```

### Generate the Python package

Run this command to generate the Python distribution archive:
```
make
```

### Upload to the Python Package Index

Install the dependencies required for uploading to the index:

```
pip install --upgrade twine
```

Upload to PyPI:

```
make upload
```
## Build and release itsimodels packages automatically
- On the left sidebar, select CI/CD > Pipelines. 
- Select Run Pipeline.
- In the Run for branch name select the branch to run the pipeline for.
- Select Run pipeline.
- base_stage job will run automatically
- sast and whitesource_python are manual jobs that do not need to be triggered if you are trying to release the package on PyPi.
- After successfully completion of previous jobs you have to click on the Settings icon of `build` job to fill variables for providing username and password
- Fill the data as follows
    ```text
    Key: username
    Value: <username of PYPI> 
    ```
    ```text
    Key: password
    Value: <password of PYPI> 
    ```
- Click on `Trigger this manual action` to start the pipeline
- Please wait for the `build` job to complete
