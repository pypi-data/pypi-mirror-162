import os
import socket
import time
import uuid


class LockUtils:
    @classmethod
    def get_pid(cls):
        return os.getpid()

    @classmethod
    def get_hostname(cls):
        return socket.gethostname()

    @classmethod
    def get_mac_address(cls):
        return hex(uuid.getnode())

    # Returns name of the lock owner.
    # With containers, chances of process id being same are quite high.
    # In fact, if your program is main docker process, its process id will mostly be 1.
    # Even with machines, there is a possibility, though rare, that two processes
    # running on two different machines will have same process id.
    # get_lock_owner is "process_id:mac_id:hostname"
    @classmethod
    def get_lock_owner(cls):
        return f"{LockUtils.get_pid()}:{LockUtils.get_mac_address()}:{LockUtils.get_hostname()}"

    @classmethod
    def get_epochtime_in_millis(cls):
        MILLION = 1000000
        return int(time.time_ns()/MILLION)
