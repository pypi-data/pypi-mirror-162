import pytest

from b_aws_testing_framework.credentials import Credentials
from b_cfn_opensearch_index_layer.opensearch_client import OpensearchClient
from b_cfn_opensearch_index_tests.integration.infrastructure.main_stack import MainStack


@pytest.fixture(scope='session')
def opensearch_client() -> OpensearchClient:
    opensearch_endpoint = MainStack.get_output(MainStack.OPENSEARCH_DOMAIN_ENDPOINT)

    return OpensearchClient(
        boto3_session=Credentials().boto_session,
        opensearch_endpoint=opensearch_endpoint
    )


__all__ = [
    'opensearch_client'
]
