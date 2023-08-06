import os
import time


# TODO: move out of here
class Discovery:
    @classmethod
    def run(cls):
        from .scheduler_lock_job import SchedulerLockJob
        if SchedulerLockJob.can_execute_task():
            print(f"*** running discovery job, process: {os.getpid()}, time: {time.asctime()} ***")


class JobX:
    @classmethod
    def run(cls):
        from .scheduler_lock_job import SchedulerLockJob
        if SchedulerLockJob.can_execute_task():
            print(f"*** running JobX job, process: {os.getpid()}, time: {time.asctime()} ***")


class JobY:
    @classmethod
    def run(cls):
        from .scheduler_lock_job import SchedulerLockJob
        if SchedulerLockJob.can_execute_task():
            print(f"*** running JobY job, process: {os.getpid()}, time: {time.asctime()} ***")


class JobsMaster:
    @classmethod
    def get_all(cls):
        return [
            [
                Discovery.run,
                'interval',
                1,
                'run_discovery'
            ],
            [
                JobX.run,
                'interval',
                1,
                'run_jobx'
            ],
            [
                JobY.run,
                'interval',
                1,
                'run_joby'
            ]
        ]
