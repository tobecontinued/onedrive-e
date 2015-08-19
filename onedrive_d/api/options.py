class NameConflictBehavior:
    RENAME = 'rename'
    REPLACE = 'replace'
    FAIL = 'fail'
    DEFAULT = FAIL


class AsyncOperationStatuses:
    NOT_STARTED = 'notStarted'
    IN_PROGRESS = 'inProgress'
    COMPLETED = 'completed'
    UPDATING = 'updating'
    FAILED = 'failed'
    DELETE_PENDING = 'deletePending'
    DELETE_FAILED = 'deleteFailed'
    WAITING = 'waiting'
