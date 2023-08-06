from .database_lock import DatabaseLock
from django.db import connection, transaction


# This class is pretty much same as DatabaseLock except that
# it uses transaction level advisory lock which ensures that
# lock acquisition and lock lease renewal are mutually exclusive
# operations as far as all the database calls are concerned.
# This will work ONLY with Postgres
class DatabaseAdvisoryLock(DatabaseLock):
    def __init__(self, name, lease_time, record_id):
        super(DatabaseAdvisoryLock, self).__init__(name, lease_time, record_id)
        self.advisory_lock_query = f"SELECT pg_advisory_xact_lock({self.record_id})"

    def __acquire_lock__(self):
        with transaction.atomic():
            cursor = connection.cursor()
            cursor.execute(self.advisory_lock_query)
            return self.__do_acquire_lock__()

    def renew_lease(self):
        with transaction.atomic():
            cursor = connection.cursor()
            cursor.execute(self.advisory_lock_query)
            return self.__do_renew_lease__()
