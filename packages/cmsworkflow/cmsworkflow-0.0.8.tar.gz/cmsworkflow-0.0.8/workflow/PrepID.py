"""
File       : PrepID.py
Author     : Hasan Ozturk <haozturk AT cern dot com>
Description: PrepID class which provides all the information needed in prepID level.
"""

from workflow.utils.WebTools import getResponse
from workflow.Workflow import Workflow
from workflow.CacheableBase import CacheableBase
from workflow.clients.JIRAClient import JIRAClient
import operator


class PrepID(CacheableBase):

    def __init__(self, prepID, url='cmsweb.cern.ch'):
        """
        Initialize the PrepID class
        :param str prepID: is the name of the prepID
        :param str url: is the url to fetch information from
        """
        self.prepID = prepID
        self.url = url

    def getWorkflows(self):
        """
        :param None
        :returns: list of Workflow objects under the given prepID
        :rtype: list of Workflow objects
        """
        data = getResponse(url=self.url,
                           endpoint='/couchdb/reqmgr_workload_cache/_design/ReqMgr/_view/byprepid?key="%s"' % (
                               self.prepID),
                           param='')
        rows = data['rows']
        workflows_s = [row['id'] for row in rows] # list of strings
        workflows = [Workflow(workflow) for workflow in workflows_s] # list of Workflow objects
        return workflows

    def getOriginalWorkflow(self):
        """
        :param None
        :returns: the original workflow of the given prepID
                : The original workflow is the oldest active workflow
        :rtype: Workflow object
        """
        workflows = self.getWorkflows()
        activeWorkflows = self.removeRejectedWorkflows(workflows)
        return max(activeWorkflows, key=operator.attrgetter("age"))

    def getRecentWorkflows(self):
        """
        :param None
        :returns: the most recent workflow(s) under the given prepID. These workflows are the ones for which we need to
                  take action, i.e. they are the ones for which no ACDC/recovery is created.
                  For instance, if there is only one (original) workflow, then that should be returned.
                  If there is one original, 3 ACDC0 and 2 ACDC1 and 2 ACDC2 workflows, then the 2 ACDC2s should be returned.
        :rtype: list of Workflow objects
        """
        originalWorkflow = self.getOriginalWorkflow()
        if originalWorkflow.getRequestType() == 'ReReco':
            return self.getRecentWorkflowsReReco()
        else:
            return self.getRecentWorkflowsMC()

    def getRecentWorkflowsMC(self):
        """
        :param None
        :returns: the most recent workflow(s) under the given prepID. It covers the MC workflows
        :rtype: list of Workflow objects
        """
        workflows = self.getWorkflows()
        activeWorkflows = self.removeRejectedWorkflows(workflows)

        # Populate the parentWorkflows, i.e. the ones for which an ACDC/recovery is created
        parentWorkflowNames = set()
        for workflow in activeWorkflows:
            parentWorkflowName = workflow.getParentWorkflowName()
            if parentWorkflowName:
                parentWorkflowNames.add(parentWorkflowName)

        recentWorkflows = []
        for workflow in activeWorkflows:
            if workflow.workflowName not in parentWorkflowNames:
                recentWorkflows.append(workflow)

        return recentWorkflows

    def getRecentWorkflowsReReco(self):
        """
        :param None
        :returns: the most recent workflow(s) under the given prepID. This function covers the special cases for ReReco
                  workflows such as recovery workflows which are different from regular ACDCs.
        :rtype: list of Workflow objects
        """
        recentWorkflows = []
        youngestWorkflow = self.getYoungestWorkflow()
        if youngestWorkflow.isRecovery():
            # If the youngest workflow is a recovery, then return the latest recovery workflows
            workflows = self.getWorkflows()
            activeWorkflows = self.removeRejectedWorkflows(workflows)

            for workflow in activeWorkflows:
                if workflow.isRecovery():
                    # A lazy workaround: Latest recovery workflows are submitted more or less  at the same time.
                    # Here, we return all recovery workflows in a 1 hour time window based on the youngest one
                    if youngestWorkflow.getAge() - workflow.getAge() < 3600:
                        recentWorkflows.append(workflow)
            return recentWorkflows
        else:
            # if youngest workflow is not a recovery, then regular MC function works
            return self.getRecentWorkflowsMC()

    def getLabels(self):
        """
        :param: None
        :returns: list of labels of the given prepID which are in sync with JIRA
        :rtype: list of strings
        """
        JC = JIRAClient()
        tickets = JC.find({'prepID': self.prepID})
        if len(tickets) == 0:
            ## TODO: Create a ticket for every workflow in assistance (Checkor module)
            print("There is no JIRA ticket for %s" % self.prepID)
            labels = []
        else:
            ## pick up the last one
            print ("There is at least one JIRA ticket for %s, taking the last one" % self.prepID)
            ticket = sorted(tickets, key=lambda t: JC.getTicketCreationTime(t))[-1]
            labels = ticket.fields.labels

        return labels

    def getCampaigns(self):
        """
        :param None
        :returns: campaigns of the given prepID
        :rtype: list of strings
        """
        pass

    def getPrimaryDataset(self):
        """
        :param None
        :returns: PD of the given prepID
        :rtype: string
        """
        pass

    def getSecondaryDatasets(self):
        """
        :param None
        :returns: secondary datasets of the given prepID
        :rtype: list of strings
        """
        pass

    def getPrimaryDatasetLocation(self):
        """
        :param None
        :returns: Location(s) of the PD
        :rtype: To be discussed (PD could be distributed over the grid)
        """
        pass

    def getSecondaryDatasetsLocation(self):
        """
        :param None
        :returns: Location(s) of the SD
        :rtype: To be discussed (SD could be distributed over the grid)
        """
        pass

    def getErrors(self):
        """
        :param None
        :returns: a dictionary containing error codes and number of failed jobs for each task/step in the following format::
                  {task: {errorcode: {site: failed_job_count}}}
        :rtype: dict
        """
        pass

    def getFailureRate(self):
        """
        :param None
        :returns: a dictionary containing failure rates for each task/step in the following format::
                  {task: failure_rate}
        :rtype: dict
        """
        pass

    # Helper functions
    def filterWorkflowsByStatus(self, workflows, status):
        """
        :param list of Workflows
        :returns: workflows in the given status
        :rtype: list of Workflow objects
        """

        for workflow in workflows:
            if workflow.getReqMgrStatus() != status:
                workflows.remove(workflow)
        return workflows

    def removeRejectedWorkflows(self,workflows):
        """
        :param list of Workflows
        :returns: removes the inactive workflows in the given list and returns the updated list
        :rtype: list of Workflow objects
        """
        inactiveStates = ["aborted",
                          "aborted-archived",
                          "rejected",
                          "rejected-archived"]
        for workflow in workflows:
            status = workflow.getReqMgrStatus()
            if status in inactiveStates:
                workflows.remove(workflow)
        return workflows

    # Write a unit test for this function
    def getYoungestWorkflow(self):
        """
        :param None
        :returns: returns the youngest workflow under given prepID
        :rtype: Workflow object
        """
        workflows = self.getWorkflows()
        activeWorkflows = self.removeRejectedWorkflows(workflows)
        return min(activeWorkflows, key=operator.attrgetter("age"))



