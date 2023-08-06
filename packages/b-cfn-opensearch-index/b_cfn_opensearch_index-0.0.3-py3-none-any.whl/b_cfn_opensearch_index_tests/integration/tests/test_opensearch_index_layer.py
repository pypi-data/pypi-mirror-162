import json

import pytest
from b_aws_testing_framework.credentials import Credentials
from botocore.response import StreamingBody

from b_cfn_opensearch_index_tests.integration.infrastructure.main_stack import MainStack


@pytest.mark.skip()
def test_RESOURCE_lambda_layer_WITH_deployed_lambda_function_1_EXPECT_execution_successful():
    """
    Test the OpensearchIndexLayer validity and functionality.

    :return: No return.
    """

    # Create client for lambda service.
    lambda_client = Credentials().boto_session.client('lambda')

    # Create lambda payload.
    test_data = {
        'OpensearchEndpoint': MainStack.get_output(MainStack.OPENSEARCH_DOMAIN_ENDPOINT)
    }

    # Invoke specific lambda function.
    response = lambda_client.invoke(
        FunctionName=MainStack.get_output(MainStack.FUNCTION1_NAME),
        InvocationType='RequestResponse',
        Payload=json.dumps(test_data)
    )

    # Parse the result.
    payload: StreamingBody = response['Payload']
    data = [item.decode() for item in payload.iter_lines()]
    data = json.loads(''.join(data))

    # Checking does response data from lambda match test data.
    # If assertion pass means lambda invocation succeeded.
    assert data == test_data, data
