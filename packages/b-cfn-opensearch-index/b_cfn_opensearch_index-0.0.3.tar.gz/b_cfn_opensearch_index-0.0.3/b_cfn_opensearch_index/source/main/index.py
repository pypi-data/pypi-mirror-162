import json
import logging

import boto3
import botocore
from botocore.exceptions import ClientError
from b_aws_cf_response.cfresponse import CfResponse

from .action import Actions, ActionResult


logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info(f'Version of boto3 lib: {boto3.__version__}.')
logger.info(f'Version of botocore lib: {botocore.__version__}.')


def __handle(event, context) -> ActionResult:
    """
    Handles incoming event by invoking a specific action according 
    to a request type.

    :param event: Invocation event.
    :param context: Invocation context.

    :return: Requested action result.
    """

    serialized_event = json.dumps(
        event,
        default=lambda o: '<not serializable>'
    )
    logger.info(f'Got new request. Event: {serialized_event}.')

    action = Actions(event)
    action_handlers = {
        'Create': action.create,
        'Update': action.update,
        'Delete': action.delete
    }

    request_type = event['RequestType']
    if request_type not in action_handlers:
        raise KeyError(f'Unsupported request type! Type: {event["RequestType"]}')

    action_handler = action_handlers[request_type]

    return action_handler()


def handler(event, context) -> None:
    """
    Handles incoming event.

    :param event: Invocation event.
    :param context: Invocation context.

    :return: No return.
    """
    response = CfResponse(event, context)

    try:
        data, resource_id = __handle(event, context)
        response.respond(
            status=CfResponse.CfResponseStatus.SUCCESS,
            data=data,
            resource_id=resource_id
        )
    except ClientError as ex:
        err_msg = f'{repr(ex)}:{ex.response}'
        response.respond(
            status=CfResponse.CfResponseStatus.FAILED,
            status_reason=err_msg
        )
    except Exception as ex:
        response.respond(
            status=CfResponse.CfResponseStatus.FAILED,
            status_reason=repr(ex)
        )
