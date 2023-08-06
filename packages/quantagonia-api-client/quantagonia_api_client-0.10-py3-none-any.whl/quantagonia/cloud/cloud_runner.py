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

    def _solveParseArgs(self, **kwargs):

        # default values
        poll_frequency: float = 1
        timeout: float = 14400

        # parse args
        if "poll_frequency" in kwargs:
            poll_frequency = kwargs["poll_frequency"]
        if "poll_frequency" in kwargs:
            timeout = kwargs["timeout"]

        solver_log = SolverLog() 

        return poll_frequency, timeout, solver_log

    def waitForJob(self, jobid: int, poll_frequency: float, timeout: float, solver_log: SolverLog) -> JobStatus:

        printed_created = False
        printed_running = False
        for t in range(0,int(timeout/poll_frequency)):

            sleep(poll_frequency)

            status = self.https_client.checkJob(jobid=jobid)
            if not self.suppress_log:
                solver_log.updateLog(self.https_client.getCurrentLog(jobid=jobid))

            if status == JobStatus.finished:
                return JobStatus.finished
            elif status == JobStatus.error:
                return JobStatus.error
            elif status == JobStatus.created:
                if not self.suppress_log:
                    if not printed_created:
                        printed_created = True
                        print("Waiting for a free slot in the queue.", end="", flush=True)
                        solver_log.nextTimeAddNewLine()
                    else:
                        print(".", end="", flush=True)

            elif status == JobStatus.running:
                if not printed_running and not self.suppress_log:
                    printed_running = True
                    print(f"\nJob {jobid} unqueued, processing...")

                    solver_log.nextTimeAddNewLine()

        return JobStatus.timeout

    async def waitForJobAsync(self, jobid: int, poll_frequency: float, timeout: float, solver_log: SolverLog) -> JobStatus:

        printed_created = False
        printed_running = False
        for t in range(0,int(timeout/poll_frequency)):

            await asyncio.sleep(poll_frequency)

            status = await self.https_client.checkJobAsync(jobid=jobid)
            if not self.suppress_log:
                solver_log.updateLog(await self.https_client.getCurrentLogAsync(jobid=jobid))

            if status == JobStatus.finished:
                return JobStatus.finished
            elif status == JobStatus.error:
                return JobStatus.error
            elif status == JobStatus.created:
                if not self.suppress_log:
                    if not printed_created:
                        printed_created = True
                        print("Waiting for a free slot in the queue.", end="", flush=True)
                        solver_log.nextTimeAddNewLine()
                    else:
                        print(".", end="", flush=True)

            elif status == JobStatus.running:
                if not printed_running and not self.suppress_log:
                    printed_running = True
                    print(f"\nJob {jobid} unqueued, processing...")

                    solver_log.nextTimeAddNewLine()

        return JobStatus.timeout

    def solve(self, problem_file: str, spec: dict, **kwargs):
        
        poll_frequency, timeout, solver_log = self._solveParseArgs(**kwargs)

        jobid = self.https_client.submitJob(problem_file=problem_file, spec=spec)
        if not self.suppress_log:
            print(f"Queued job with jobid: {jobid} for execution in the Quantagonia cloud...\n")

        status: JobStatus = self.waitForJob(jobid=jobid, poll_frequency=poll_frequency, timeout=timeout, solver_log=solver_log)

        if status is not JobStatus.finished:
            raise Exception(f"Job with jobid {jobid} error. Status of the job: {status}")
        else:
            if not self.suppress_log:
                print(f"Finished processing job {jobid}...")

        res = self.https_client.getResults(jobid=jobid)
        if not self.suppress_log:
            solver_log.updateLog(res['solver_log'])

        return {
            'solver_log' : res['solver_log'],
            'solution_file' : res['solution_file']
        }

    async def solveAsync(self, problem_file: str, spec: dict, **kwargs):
        
        poll_frequency, timeout, solver_log = self._solveParseArgs(**kwargs)

        jobid = await self.https_client.submitJobAsync(problem_file=problem_file, spec=spec)
        if not self.suppress_log:
            print(f"Queued job with jobid: {jobid} for execution in the Quantagonia cloud...")

        status: JobStatus = await self.waitForJobAsync(jobid=jobid, poll_frequency=poll_frequency, timeout=timeout, solver_log=solver_log)

        if status is not JobStatus.finished:
            raise Exception(f"Job with jobid {jobid} error. Status of the job: {status}")
        else:
            if not self.suppress_log:
                print(f"Finished processing job {jobid}...")

        res = await self.https_client.getResultsAsync(jobid=jobid)
        if not self.suppress_log:
            solver_log.updateLog(res['solver_log'])

        return {
            'solver_log' : res['solver_log'],
            'solution_file' : res['solution_file']
        }