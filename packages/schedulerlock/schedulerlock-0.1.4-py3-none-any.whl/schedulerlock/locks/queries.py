class Queries:
    __table__ = "scheduler_lock"
    DELETE = f""" DELETE FROM {__table__} WHERE lock_id = %s """
    INSERT = f""" INSERT INTO {__table__} (lock_id, name, valid_until) VALUES (%s, %s, %s)"""
    SELECT = f""" SELECT lock_id, name, valid_until FROM {__table__} WHERE lock_id = %s"""
    SELECT_4_RENEW = f""" SELECT lock_id, name, valid_until, fencing_token_id FROM {__table__} """\
                     """ WHERE lock_id = %s AND name = %s"""
    UPDATE = f""" UPDATE {__table__} SET valid_until = %s WHERE lock_id = %s AND name = %s"""
