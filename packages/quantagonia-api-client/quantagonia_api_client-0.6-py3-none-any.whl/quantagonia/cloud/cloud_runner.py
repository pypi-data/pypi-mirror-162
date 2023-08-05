from io import UnsupportedOperation
import sys, os
import asyncio
from time import sleep
from enum import Enum

from quantagonia.cloud.solver_log import SolverLog
from quantagonia.cloud.specs_https_client import SpecsHTTPSClient, JobStatus
from quantagonia.cloud.specs_enums import *
from quantagonia.runner import Runner
from quantagonia.enums import HybridSolverServers

class CloudRunner(Runner):
    def __init__(self, api_key: str, server: HybridSolverServers = HybridSolverServers.PROD, suppress_log : bool = False):
        self.https_client = SpecsHTTPSClient(api_key=api_key, target_server=server)
        self.suppress_log = suppress_log

    def wait_for_job(self, jobid: int, poll_frequency: float, timeout: float, solver_log: SolverLog) -> JobStatus:
        for t in range(0,int(timeout/poll_frequency)):
            sleep(poll_frequency)

            status = self.https_client.check_job(jobid=jobid)
            if not self.suppress_log:
                solver_log.update_log(self.https_client.get_current_log(jobid=jobid))

            if status == JobStatus.finished:
                return JobStatus.finished
            elif status == JobStatus.error:
                return JobStatus.error
            elif status == JobStatus.running or status == JobStatus.created:
                continue

        return JobStatus.timeout

    # Python 3.10: -> dict | asyncio.Future
    def solve(self, problem_file: str, spec: dict, blocking : bool, **kwargs):

        # default values
        poll_frequency: float = 1
        timeout: float = 14400

        # parse args
        if "poll_frequency" in kwargs:
            poll_frequency = kwargs["poll_frequency"]
        if "poll_frequency" in kwargs:
            timeout = kwargs["timeout"]

        solver_log = SolverLog() 

        if not blocking:
            raise UnsupportedOperation("Non-blocking execution not yet implemented.")

        jobid = self.https_client.submit_job(problem_file=problem_file, spec=spec)
        if not self.suppress_log:
            print(f"Submitted job with jobid: {jobid} for execution in the Quantagonia cloud...\n")
        status: JobStatus = self.wait_for_job(jobid=jobid, poll_frequency=poll_frequency, timeout=timeout, solver_log=solver_log)

        if status is not JobStatus.finished:
            raise Exception(f"Job with jobid {jobid} error. Status of the job: {status}")
        res = self.https_client.get_results(jobid=jobid)
        if not self.suppress_log:
            solver_log.update_log(res['solver_log'])

        return {
            'solver_log' : res['solver_log'],
            'solution_file' : res['solution_file']
        }
