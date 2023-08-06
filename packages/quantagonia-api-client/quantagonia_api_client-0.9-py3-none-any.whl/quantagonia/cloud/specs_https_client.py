import json
import os
import uuid
import requests

from quantagonia.cloud.specs_enums import *
from quantagonia.enums import HybridSolverServers

class SpecsHTTPSClient():
    """ client class for qqvm server """
    def __init__(self, api_key: str, target_server: HybridSolverServers = HybridSolverServers.PROD) -> None:
        """ """
        self.api_key = api_key
        self.server = target_server.value

    def _submitJob(self, problem_file: str, spec: dict) -> uuid:
        with open(problem_file, 'rb') as file:
            files = {'file': (os.path.basename(problem_file), file, 'text/plain')}
            response = requests.post(self.server + SpecsEndpoints.submitjob, files=files, params={"spec" : json.dumps(spec)}, headers={"X-api-key" : self.api_key})

        if not response.ok:
            raise RuntimeError(f"Request error. status: {response.status_code}, text: {response.text}")
        return response.json()['jobid']

    def _checkJob(self, jobid: uuid) -> str:
        params = {'jobid': str(jobid)}
        response = requests.get(self.server + SpecsEndpoints.checkjob, params=params, headers={"X-api-key" : self.api_key})
        
        if not response.ok:
            raise RuntimeError(f"Request error. status: {response.status_code}, text: {response.text}")
        return response.json()['status']

    def _getCurrentLog(self, jobid: uuid) -> str:
        params = {'jobid': str(jobid)}
        response = requests.get(self.server + SpecsEndpoints.getcurlog, params=params, headers={"X-api-key" : self.api_key})

        if not response.ok:
            raise RuntimeError(f"Request error. status: {response.status_code}, text: {response.text}")
        return response.text

    def _getResults(self, jobid: uuid) -> dict:
        params = {'jobid': str(jobid)}
        response = requests.get(self.server + SpecsEndpoints.getresults, params=params, headers={"X-api-key" : self.api_key})
        
        if not response.ok:
            raise RuntimeError(f"Request error. status: {response.status_code}, text: {response.text}")
        return {
            "solver_log" : response.json()['solver_log'],
            "solution_file" : response.json()['solution_file']
        }

    ### blocking interface
    def submitJob(self, problem_file: str, spec: dict) -> uuid:
        return self._submitJob(problem_file, spec)

    def checkJob(self, jobid: uuid) -> str:
        return self._checkJob(jobid)

    def getCurrentLog(self, jobid: uuid) -> str:
        return self._getCurrentLog(jobid)

    def getResults(self, jobid: uuid) -> dict:
        return self._getResults(jobid)

    ### non-blocking interface
    async def submitJobAsync(self, problem_file: str, spec: dict) -> uuid:
        return self._submitJob(problem_file, spec)

    async def checkJobAsync(self, jobid: uuid) -> str:
        return self._checkJob(jobid)

    async def getCurrentLogAsync(self, jobid: uuid) -> str:
        return self._getCurrentLog(jobid)

    async def getResultsAsync(self, jobid: uuid) -> dict:
        return self._getResults(jobid)