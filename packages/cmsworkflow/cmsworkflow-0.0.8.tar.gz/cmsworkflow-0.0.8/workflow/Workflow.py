"""
File       : Workflow.py
Author     : Hasan Ozturk <haozturk AT cern dot com>
Description: Workflow class provides all the information needed for the filtering of workflows in assistance manual.
"""

from workflow.utils.WebTools import getResponse
from workflow.utils.SearchTools import findKeys

from workflow.CacheableBase import CacheableBase,cached_json

import time

class Workflow(CacheableBase):

    def __init__(self, workflowName, url='cmsweb.cern.ch'):
        """
        Initialize the Workflow class
        :param str workflowName: is the name of the workflow
        :param str url: is the url to fetch information from
        """
        super( Workflow , self).__init__()
        self.workflowName = workflowName
        self.url = url
        self.workflowParams = self.getWorkflowParams()
        self.requestType = self.workflowParams.get('RequestType')
        self.age = self.getAge()
        self.tasks = self.getTaskNames()
        
    def serialize(self):
        """
        the output of this method is used by the rest-api in the "AdditionalInfo" field
        """
        return { 
            'PrepID':self.getPrepID()
        }

    def __str__(self):
        return 'workflowinfo_%s' % self.workflowName
        
    @cached_json('workflow_params')
    def getWorkflowParams(self):

        """
        Get the workflow parameters from ReqMgr2.
        See the `ReqMgr 2 wiki <https://github.com/dmwm/WMCore/wiki/reqmgr2-apis>`_
        for more details.
        :returns: Parameters for the workflow from ReqMgr2.
        :rtype: dict
        """

        try:
            result = getResponse(url=self.url,
                                 endpoint='/reqmgr2/data/request/',
                                 param=self.workflowName)

            for params in result['result']:
                for key, item in list(params.items()):
                    if key == self.workflowName:
                        self.workflowParams = item
                        return item

        except Exception as error:
            print('Failed to get workflow params from reqmgr for %s ' % self.workflowName)
            print(str(error))

    def getTasksParams(self, getKey: str):

        """
        Get all tasks parameters from ReqMgr2.
        :returns: for each task, the getKey item in the workflowParams dictionary
        :rtype: dict
        """

        output = {}

        ### FIMXE: check for each instead of harcoding
        if 'StepChain' == self.requestType: identifier = 'Step'
        elif 'TaskChain' == self.requestType: identifier = 'Task'
        elif 'ReReco' == self.requestType: identifier = False
        else:
            raise Exception("No steps or tasks found in this workflow.")

        # if MC
        if identifier:

            # WMagent-tasks
            for WM_agent_task in self.tasks:

                # loop over all ReqMgr-tasks e.g. Step1, Step2, ...
                i = 1
                found = False
                while not found:
                    try:
                        ReqMgr_task = self.workflowParams[identifier+str(i)][identifier+'Name']
                        if ReqMgr_task in WM_agent_task.split("/")[-1]:
                            found = True 
                            key = self.workflowParams[identifier+str(i)][getKey]
                            output.update({WM_agent_task: key})
                        else: i+= 1
                    # reached the end
                    except KeyError:
                        break

        # if ReReco, there are no multiple tasks/steps
        else:
            key = self.workflowParams[getKey]
            # WMagent-tasks
            for WM_agent_task in self.tasks: output.update({WM_agent_task: key})

        return output

    def getPrepID(self):
        """
        :param: None
        :returns: PrepID
        :rtype: string
        """
        return self.workflowParams.get('PrepID')

    def filterTaskNames(self, tasks):
        """
        :param: list of tasks (strings)
        :returns: list of task names filtered.
        :rtype: list of str
        """

        filteredTasks = []
        for task in tasks:
            if any([v in task.lower() for v in ['logcollect','cleanup']]): continue
            filteredTasks.append(task)
        return filteredTasks

    def getTaskNames(self):
        """
        :param: None
        :returns: list of Tasks of the given workflow.
                  N.B.: these are not all the steps in a StepChain, these are all the tasks
                  for which error codes exist, i.e. in the WM agent json, used by getErrors,
                  they are the AgentJobInfo tasks.
        :rtype: list of str
        """
        tasks = list(self.getJobStats().keys())
        tasks = self.filterTaskNames(tasks)

        return tasks

    def getNumberOfEvents(self):
        """
        :param: None
        :returns: Number of events requested
        :rtype: int
        """
        return self.workflowParams.get('TotalInputEvents')

    def getRequestType(self):
        """
        :param: None
        :returns: Request Type
        :rtype: string
        """

        return self.workflowParams.get('RequestType')

    def getSiteWhitelist(self):
        """
        :param: None
        :returns: SiteWhitelist
        :rtype: string
        """

        return self.workflowParams.get('SiteWhitelist')

    def getCampaigns(self):
        """
        Function to get the list of campaigns that this workflow belongs to
        :param: None
        :returns: list of campaigns that this workflow belongs to
        :rtype: list of strings
        """

        return findKeys('Campaign', self.workflowParams)

    def getTasksCampaigns(self):
        """
        Function to get the campaign for each task
        :param: None
        :returns: dictionary with keys being task names, items being the campaigns
        :rtype: dict of strings
        """
        return self.getTasksParams('Campaign')

    ## Get runtime related values

    def getAge(self):
        """
        Number of days since the creation of the workflow
        :param: None
        :returns: Age of the workflow
        :rtype: float
        """
        if 'RequestTransition' not in self.workflowParams:
            return "Age unknown"
        for transition in self.workflowParams['RequestTransition']:
            if transition['Status'] == 'assignment-approved':
                return int(time.time()) - int(transition['UpdateTime'])

        raise Exception("Failed to get the age of workflow: The workflow has no assignment-approved history")

    def getJobStats(self):
        """
        :param None
        :returns: a dictionary containing number of successful and failed jobs for each task/step in the following format::
                  {<taskName>: 
                    nSuccess: X,
                    nFailure: Y
                  }
        :rtype: dict
        """

        response = getResponse(url=self.url,
                             endpoint='/wmstatsserver/data/request/',
                             param=self.workflowName)
        
        jobStatsPerTask = {}
        if not response['result']:
            return jobStatsPerTask

        try:
            for agentName, agentData in response['result'][0].get(self.workflowName)['AgentJobInfo'].items():
                for taskName, taskData in agentData['tasks'].items():
                    # Some tasks such as LogCollect, Cleanup etc. don't have job info
                    # TODO: Decide whether we should ignore such tasks or not. Ignore for now
                    if 'status' not in  taskData:
                        continue
                    else:
                        taskStatus = taskData['status']
                    nSuccess = taskStatus['success'] if 'success' in taskStatus else 0
                    nFailure = sum(taskStatus['failure'].values()) if 'failure' in taskStatus else 0
                    if taskName in jobStatsPerTask:
                        jobStatsPerTask[taskName]['nSuccess'] += nSuccess
                        jobStatsPerTask[taskName]['nFailure'] += nFailure
                    else:
                        jobStatsPerTask[taskName] = {'nSuccess': nSuccess, 'nFailure': nFailure}
            return jobStatsPerTask
        except Exception as e:
            print(str(e))
            return {}


    def getFailureRate(self):
        """
        :param None
        :returns: a dictionary containing failure rates for each task/step in the following format::
                  {task: failure_rate}
        :rtype: dict
        """
        failureRatePerTask = {}
        jobStats = self.getJobStats()
        try:
            for taskName, stats in jobStats.items():
                # Avoid division by zero, although we shouldn't have such data
                if stats['nFailure'] == 0 and stats['nSuccess'] == 0:
                    failureRatePerTask[taskName] = -1
                else:
                    failureRatePerTask[taskName] = stats['nFailure'] / (stats['nFailure'] + stats['nSuccess'])
            return failureRatePerTask
        except Exception as e:
            print(str(e))
            return {}
   

    ## Get request related values

    def getPrimaryDataset(self):
        """
        :assumption: every production workflow reads just one PD
        :param: None
        :returns: the name of the PD that this workflow reads
        :rtype: list
        """

        return findKeys('InputDataset', self.workflowParams)

    def getPrimaryDatasetLocation(self):
        """
        :assumption: every production workflow reads just one PD
        :param: None
        :returns: list of RSEs hosting the PD
        :rtype: list of strings
        """
        pass

    def getSecondaryDatasets(self):
        """
        :info: a workflow can read more than one secondary datasets
        :param: None
        :returns: list of the names of PUs that this workflow reads
        :rtype: list of strings
        """

        return findKeys('MCPileup', self.workflowParams)

    def getSecondaryDatasetsLocation(self):
        """
        :info: a workflow can read more than one secondary datasets
        :param: None
        :returns: dictionary containing PU name and location pairs
        :rtype: dict
        """
        pass

    def getPrimaryAAA(self):
        """
        Function to get the primaryAAA/TrustSitelists value of the request (Either True or False)
        :param: None
        :returns: the primaryAAA/TrustSitelists value of the request (Either True or False)
        :rtype: boolean
        """
        return self.workflowParams['TrustSitelists']

    def getSecondaryAAA(self):
        """
        Function to get the secondaryAAA/TrustPUSitelists value of the request (Either True or False)
        :param: None
        :returns: the secondaryAAA/TrustPUSitelists value of the request (Either True or False)
        :rtype: boolean
        """
        return self.workflowParams['TrustPUSitelists']

    # Write a unit test for this function
    def getReqMgrStatus(self):
        """
        :param None
        :returns: the ReqMgr status of the workflow
        :rtype: string
        """
        return self.workflowParams["RequestStatus"]

    def getParentWorkflowName(self):
        """
        :param None
        :returns: the parent workflow. Parent workflow is the one for which the ACDC/recovery is created
        :rtype: Workflow object
        """
        if 'InitialTaskPath' in self.workflowParams:
            initialTaskPath = self.workflowParams['InitialTaskPath']
            parentWorkflowName = initialTaskPath.split('/')[1]
            return parentWorkflowName
        else:
            return None

    # Write a unit test for this function
    def isRecovery(self):
        """
        :param None
        :returns: True if the given workflow is a recovery workflow, False otherwise
                  Note that recovery workflows are different from regular ACDC workflows
        :rtype: bool
        """
        requestType = self.getRequestType()
        if requestType == 'Resubmission':
            if self.workflowParams['OriginalRequestType'] == 'ReReco':
                if 'ACDC' in self.workflowName:
                    return False
                else:
                    return True
            else:
                return False
        else:
            return False

    # Disable caching for now.
    # TODO: We shouldn't need to change the source code to enable/disable caching. Make this configurable.
    # @cached_json('workflow_errors')
    def getErrors(self, getUnreported=True):
        """
        Get the useful status information from a workflow
        :param bool getUnreported: Get the unreported errors from ACDC server
        :returns: a dictionary containing error codes in the following format::
              {step: {errorcode: {site: number_errors}}}
        :rtype: dict
        """

        result = getResponse(url=self.url,
                             endpoint='/wmstatsserver/data/jobdetail/',
                             param=self.workflowName)
        output = {}

        if not result['result']:
            return output

        for stepName, stepData in result['result'][0].get(self.workflowName, {}).items():
            errors = {}
            for errorCode, errorCodeData in stepData.get('jobfailed', {}).items():
                sites = {}
                for site, siteData in errorCodeData.items():
                    if siteData['errorCount']:
                        sites[site] = siteData['errorCount']

                if sites:
                    errors[errorCode] = sites

            if errors:
                output[stepName] = errors

        
        if getUnreported:
            acdcServerResponse = getResponse(url=self.url,
                                             endpoint='/couchdb/acdcserver/_design/ACDC/_view/byCollectionName',
                                             param={'key': '"%s"' % self.workflowName, 'include_docs': 'true', 'reduce': 'false'})

            if 'rows' in acdcServerResponse:
                for row in acdcServerResponse['rows']:
                    task = row['doc']['fileset_name']
                    #print('a' , task )

                    newOutput = output.get(task, {})
                    newErrorCode = newOutput.get('-2', {})
                    modified = False
                    for fileReplica in row['doc']['files'].values():
                        for site in fileReplica['locations']:
                            modified = True
                            if site in newErrorCode:
                                newErrorCode[site] += 1
                            else:
                                newErrorCode[site] = 1
                                
                    if modified:
                        newOutput['-2'] = newErrorCode
                        output[task] = newOutput

        # for step in list(output):
        #     if True in [(steptype in step) for steptype in ['LogCollect', 'Cleanup']]:
        #         output.pop(step)

        return output
