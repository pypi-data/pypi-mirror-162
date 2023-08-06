import os

from django.conf import settings

from ..locks.database_advisory_lock import DatabaseAdvisoryLock
from ..locks.database_lock import DatabaseLock
from ..locks.file_lock import FCNTLFileLock
from .all_jobs import JobsMaster


class SchedulerLockJob:
    # Am I owner of the lock
    lock_owner = False
    lock = None
    if settings.SCHEDULER_LOCK_TYPE == 'Database':
        lock = DatabaseLock(settings.SCHEDULER_LOCK_NAME, settings.SCHEDULER_LOCK_LEASE_TIME,
                            settings.SCHEDULER_LOCK_RECORD_ID)
    elif settings.SCHEDULER_LOCK_TYPE == 'Database_Advisory':
        lock = DatabaseAdvisoryLock(settings.SCHEDULER_LOCK_NAME,
                                    settings.SCHEDULER_LOCK_LEASE_TIME,
                                    settings.SCHEDULER_LOCK_RECORD_ID)
    elif settings.SCHEDULER_LOCK_TYPE == 'File':
        lock = FCNTLFileLock(os.path.join(settings.LOCK_FILE_BASE_PATH, "aistudio.lock"))
    else:
        raise Exception(f"Scheduler lock type {settings.SCHEDULER_LOCK_TYPE} not supported.")

    jobs = []

    @classmethod
    def scheduler_lock(cls):
        print(f"running scheduler_lock job, pid: {os.getpid()}, jobs: {cls.jobs}", flush=True)
        from ..apps import SchedulerlockConfig
        if not cls.lock_owner:
            if cls.lock.try_acquire_lock():
                print(f"VIOLA I {os.getpid()} am the lock owner VIOLA", flush=True)
                cls.lock_owner = True
                for mj in JobsMaster.get_all():
                    j = SchedulerlockConfig.scheduler.add_job(mj[0], mj[1], seconds=mj[2], name=mj[3])
                    print(f"adding jobs: {os.getpid()} added jobid: {j.id}", flush=True)
                    cls.jobs.append(j)
        else:
            if not cls.lock.renew_lease():
                for j in cls.jobs:
                    # we can't do remove_all_jobs, it will end up removing
                    # scheduler_lock job as well
                    print(f"removing jobs: process {os.getpid()}, removed jobid: {j.id}",
                          flush=True)
                    try:
                        SchedulerlockConfig.scheduler.remove_job(j.id)
                    except (Exception) as e:
                        str(e)
                    else:
                        print(f"removed job: process {os.getpid()}, removed jobid: {j.id}",
                              flush=True)
                cls.lock_owner = False
                cls.jobs = []

    @classmethod
    def can_execute_task(cls):
        return cls.lock.can_execute_task()
