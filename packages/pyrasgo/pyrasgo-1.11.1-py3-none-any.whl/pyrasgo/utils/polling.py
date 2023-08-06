import time

from pyrasgo import errors, schemas


def poll_operation_set_async_status(
    task_request: schemas.OperationSetAsyncTask,
    delay_start=1,
    delay_max=1.5,
    backoff_multiplier=1.5,
    verbose=False,
) -> int:
    """
    Given some task request, this function will poll the API until the task hits a terminal status.

    If operation set created successfully with no errors, return operation set id
    """
    from pyrasgo.api import Get

    get = Get()

    operations_expected = len(task_request.request.operations)
    operations_created = 0
    delay = delay_start
    while True:
        time.sleep(delay)
        task_request = get._operation_set_async_status(task_request.id)

        # Get the status of the last event
        last_event_status = task_request.events[-1].event_type

        # Let the user know if this started
        if last_event_status == 'STARTED':
            if verbose:
                print(f'Operation set task {task_request.id} has started')

        # Is this progress? Keep track.
        if last_event_status == 'PROGRESSED':
            operations_created = task_request.events[-1].message['complete']
            if verbose:
                print(f'Operation set creation: {operations_created} of {operations_expected} operations complete')

        # Is this a failure? Throw an exception
        if last_event_status == 'FAILED':
            raise errors.APIError(
                f'Operation set creation failure: {task_request.events[-1].message}; '
                f'Progress: {operations_created} / {operations_expected}'
            )

        # Is this a success? Get out of this loop
        if last_event_status == 'FINISHED':
            operation_set_id = task_request.events[-1].message['operation_set_id']
            return operation_set_id

        # Still waiting? Grab a Snickers
        if delay < delay_max:
            delay = min(delay * backoff_multiplier, delay_max)
        if verbose:
            print('Poll waiting...')
