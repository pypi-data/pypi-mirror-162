class DistributeLock:
    def can_execute_task(self):
        return True

    def try_acquire_lock(self):
        raise Exception("Not implemented")

    def renew_lease(self):
        raise Exception("Not implemented")
