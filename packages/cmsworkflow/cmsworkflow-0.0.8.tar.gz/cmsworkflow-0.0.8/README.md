# Workflow

The package to gather all the information of the workflow from different sources.
It also provides some tools/classes to interpret the information to higher level properties.
In addition needed details are stored in a database.

## Requirements

- The necessary packages are listed in `requirements.txt` file. It's recommended to create a virtual environment and run the following command to install dependencies at once:

```
pip install -r requirements.txt
```
- x509 proxy is needed to communicate with several CMS services such as ReqMgr2:
```
voms-proxy-init -voms cms
export X509_USER_PROXY=`voms-proxy-info --path`
```

## Contribution guidelines

#### 1.Clone the repository
```
git clone https://gitlab.cern.ch/CMSToolsIntegration/workflow.git
```

#### 2. Branch off from master
- Make sure that a GitLab issue is present for which you're going to make changes

```
git checkout -b <my-branch>
```

#### 3. Implement your changes

#### 4. Test your changes

- All unit tests must be successful for your PR to be accepted.
- Write new unit tests for your new changes

First build the package in development mode:
```
pip install -e .
```

Then, you can run a single unit test as follows:
```
python test/Workflow_t.py
```
#### 5. Submit PR/MR
If you are happy and confident with your changes, submit a Pull/Merge request


# PyPi Upload

Assumes that you have PyPi account and permission for this project.

1. Edit the version at `setup.py`
2. `python setup.py sdist`
3. `twine upload dist/*`



