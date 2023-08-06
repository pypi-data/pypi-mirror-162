import json
import logging

import boto3
from b_aws_cf_response import cfresponse
from b_cfn_opensearch_index_layer.opensearch_client import OpensearchClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context) -> None:
    logger.info(json.dumps(event))
    opensearch_client = OpensearchClient(
        boto3_session=boto3.Session(),
        opensearch_endpoint=event['OpensearchEndpoint']
    )
    cluster_health = opensearch_client.cat.health()
    logger.info(cluster_health)
    return event
