from .base_lock import DistributeLock
import sys
import os
from os.path import exists
from .utils import LockUtils


# FCNTLFileLock uses Python fcntl module which internally uses system calls like
# 'fcntl', 'flock' etc. These system calls are available on most flavours of Linux.
# ## Note on Azure Files ##
# In Azure, you mount 'Azure File' on Linux VMs which can be used by applications
# directly running on VMs or containers(pods) which run on these VMs. An 'Azure File'
# can be mounted using either SMB protocol or NFS protocol. With the former, fcntl.flock()
# running on more than one machine on the same file will succeed and this NO longer is
# the distributed lock. fcntl.flock() works in the expected way with SMB mounted
# Azure file as long as all the processes are running on the same machine.
# For distributed lock to work with 'Azure File', it has to be mounted with NFS and for
# that to happen, (1) 'Premium' storage account has to be created with 'File shares:' as
# the value for 'Premium account type'. (2) Azure file share you create inside this
# storage account needs to be created with 'NFS' protocol. Without the former, you don't get
# a choice to select the protocol and Azure will create file share with 'SMB' protocol.

class FCNTLFileLock(DistributeLock):
    def __init__(self, lock_file):
        # You can't do this at the top of the file. Reason is, even if
        # FCNTLFileLock never gets instantiated, moment file_lock gets
        # imported in another file, code at the top will execute and
        # program will quit if 'fcntl' module in not found which would
        # be the case on Windows. FCNTLFileLock class gets instantiated
        # only when SCHEDULER_LOCK_TYPE is 'File'.
        # Other option will be to conditionally import file_lock moddule
        # based on value of SCHEDULER_LOCK_TYPE which is not so nice.
        try:
            import fcntl
            self.lock_file = lock_file
            self.lock_file_fd = None
            print(f"Module {fcntl.__name__} imported successfully.")
        except ModuleNotFoundError as e:
            print(f"ModuleNotFoundError: {e}")
            print("This will NOT work on Windows.")
            sys.exit(1)

    def try_acquire_lock(self):
        import fcntl
        fd = None
        try:
            f_exists = exists(self.lock_file)
            if f_exists:
                open_mode = os.O_RDWR
            else:
                open_mode = os.O_RDWR | os.O_CREAT
            fd = os.open(self.lock_file, open_mode, 0o600)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            owner = LockUtils.get_lock_owner()
            print(f"{owner} owns lock on file {self.lock_file}")
            owner_bytes = bytes(owner + '\n', 'utf-8')
            os.write(fd, owner_bytes)
            os.truncate(fd, len(owner_bytes))
            self.lock_file_fd = fd
        except (IOError, OSError):
            if fd is not None:
                print(f"Lock not obtained, closing {fd}, pid: {os.getpid()}")
                os.close(fd)
            return False

        return True

    # This method actually never gets called.
    # Lock is released only when lock owner dies, shuts down etc.
    def release(self):
        import fcntl
        # Do not remove the lockfile:
        #
        #   https://github.com/benediktschmitt/py-filelock/issues/31
        #   https://stackoverflow.com/questions/17708885/flock-removing-locked-file-without-race-condition
        fcntl.flock(self.lock_file_id, fcntl.LOCK_UN)
        os.close(self.lock_file_id)

    def renew_lease(self):
        return True
