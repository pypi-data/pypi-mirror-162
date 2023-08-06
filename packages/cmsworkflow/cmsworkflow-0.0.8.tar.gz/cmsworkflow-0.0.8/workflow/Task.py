"""
File       : Task.py
Author     : Hasan Ozturk <haozturk AT cern dot com>
Description: Task class which provides all the information needed in task level.
"""

from workflow.CacheableBase import CacheableBase, cached_json
from workflow.Workflow import Workflow
from pandas import DataFrame

class Task(CacheableBase):

    def __init__(self, taskName, workflow, getUnreportedErrors=True, url='cmsweb.cern.ch'):
        """
        Initialize the Task class
        :param str taskName: is the name of the task
        :param str url: is the url to fetch information from
        """
        self.taskName = taskName
        self.url = url
        if type(workflow) == str:
            self.workflow = Workflow(workflow , getUnreportedErrors=getUnreportedErrors)
        else:
            self.workflow = workflow
        
    def getErrorsDF(self):
        """
        :param None
        :returns: an instance of pandas.DataFrame for the failed jobs. each row contains sites information and columns are error codes::
        :rtype: pandas.DataFrame
        """
        self.errors = DataFrame( self.workflow.errors[ self.taskName ] )
        
        return self.errors

    def getErrors(self):
        """
        :param None
        :returns: a dictionary containing error codes in the following format::
              {step: {errorcode: {site: number_errors}}}
        :rtype: dict
        """
        return self.workflow.errors[ self.taskName ]

    def getFailureRate(self):
        """
        :param None
        :returns: a float containing failure rate of the given task/step in the following format::
                  failure_rate
        :rtype: float
        """
        failureRate = self.workflow.getFailureRate()
        return failureRate[ self.taskName ]

    def getPrimaryAAA(self):
        """
        :param None
        :returns: if the primary AAA is on or off
        :rtype: bool
        """
        pass

    def getSecondaryAAA(self):
        """
        :param: None
        :returns: if the secondary AAA is on or off
        :rtype: bool
        """

        pass




