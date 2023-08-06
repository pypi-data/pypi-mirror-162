from django.db import models


# Django
# - adds a column 'id' automatically to the model unless some other column is
#    the primary_key.
# - allows only one column to be an AutoField. So if 'id' is automatically
#    generated as primary_key, it also is an AutoField and you can't have
#    another column marked as an AutoField.
# Logically lock_id seems a natural choice for primary_key but we want
# fencing_token_id to auto increment and that's only possible if we
# make it primary_key. But that is okay. We make lock_id 'unique' and
# that serves our purpose.
class SchedulerLock(models.Model):
    class Meta:
        db_table = "aistudio_scheduler_lock"

    lock_id = models.IntegerField(unique=True, null=False)
    # Friendly name to identify purpose of the lock, it is 'unique' as
    # two identical friendly names might be confusing
    name = models.CharField(max_length=128, unique=True, null=False)
    # Process identifying the lock owner. It is constructed as
    # process_id:mac_address:host_name. We can't just use process_id as it
    # can be the same when processes are running on different machines. In fact,
    # when process runs as the main process inside the container, chances of
    # their process_id being the same are extremely high.
    owner = models.CharField(max_length=512, unique=True, null=False)
    # Lock validity, epoch time in milliseconds
    valid_until = models.BigIntegerField(null=False)
    # https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html
    # explains what a fencing token is. It's not applicable in our context.
    # But it does help us a bit as explained below.
    # Say process1 is the lock owner and it is in the process of renewing the lock
    # lease. It gets the lock record from the database, computes new valid_until value.
    # But there is a big dealy before it can execute save() operation. In the meantime
    # some other process, say process2 checks lock validity and finds that lock is
    # stale (valid_until < current_time). It is now going to do 2 actions: delete the lock
    # record and insert a new one. In view of this, save() operation by process1 CAN
    # 1. happen before process2 deletes the lock record
    #    process1 will update the record and would think that it is the lock owner.
    #    process2 will carry out both delete and insert operations and becomes the
    #    new lock owner. Now process1 is no longer the lock owner but it thinks, it is.
    #    And it will continue to think that way till it tries to renew the lock lease.
    #    Solution to this problem is scheduled jobs first checking lock 'owner' before
    #    executing the task they are supposed to carry out.
    # 2. happen after process2 has deleted the lock record
    #    process1 by virtue of calling save() actually inserts a new lock record.
    #    When process2 tries to insert the record, it fails and doesn't get the lock.
    #    process1 continues to be lock owner and things are just fine. Just that
    #    process1 gets a new fencing_token_id thanks to insert operation.
    # 3. happen after process2 has inserted the new lock record
    #    Even in this case process1, by virtue of calling save() actually tries to
    #    insert the record rahter than updating the lock record.
    #    Reason is, when process2 inserts the lock record, fencing_token_id gets
    #    incremented. Say it becomes 102. One with process1 is still 101. So save()
    #    operation by process1 tries to insert a new record as fencing_token_id is
    #    the primary_key. But this operation will fail as lock_id in the record being
    #    inserted is the same as the one present in the table and as lock_id is
    #    unique key, this save() operation fails, the way process1 knows it no longer
    #    holds the lock.
    # So only in the first scenario, more than one process thinks, it holds the lock;
    # process2 holds the lock but process1 also thinks it is the lock owner.
    # Without the fencing token id, scenario 3 also would have resulted in a situation
    # where 2 processes think that they are the lock owners.
    # But in any case, one solution to solve this problem is: scheduled jobs
    # first check lock 'owner' from the database and compare it with the process
    # lock onwer name before executing the task they are supposed to carry out.
    # Postgres ADVISORY lock?
    # To avoid this particular race-condition problem, one process trying to renew
    # the lock lease and other trying to get hold of it, one can possibly use Postgres
    # advisory lock. Essentially methods try_acquire_lock and renew_lease of
    # 'class DatabaseLock' can execute database code within a transaction advisory lock,
    # thereby making sure, no two processes will ever have the lock or rather one will have it
    # and other will think, it also has it.
    # With advisory lock, 'can_execute_task' method will possibly not have to be called
    # by every scheduled job. Well, that may not be entirely true. Say process1 holds the
    # lock and for some reason, it is slow in renewing the lock. Process2 executes
    # below code in a Transaction advisory lock
    # - check if lock is stale (answer is YES in this case)
    # - delete the current lock
    # - acquire the lock by inserting a new lock row
    # Process2 now registers all the scheduled jobs with itself.
    # While the code in 'advisory lock' is being executed, process1 will not be able to renew
    # the lock. After process2 is done acquiring the lock, process1 tries to renew the lock,
    # fails, realizes it no longer is the lock owner and unregisteres the scheduled jobs.
    # But between the time, process2 gets the lock and process1 unregisters the jobs
    # a few jobs might execute on both the processes.
    # - With aAdivsory locking, fencing_token_id becomes redundant in our context.
    # - Also it only is available with postgres.
    fencing_token_id = models.BigAutoField(primary_key=True)
