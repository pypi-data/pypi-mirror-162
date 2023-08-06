from aws_cdk.core import Construct, Stack
from b_aws_testing_framework.tools.cdk_testing.testing_stack import TestingStack

from b_cfn_opensearch_index_tests.integration.infrastructure.functions.function1 import Function1
from b_cfn_opensearch_index_tests.integration.infrastructure.opensearch_domain_stack import OpensearchDomainStack
from b_cfn_opensearch_index_tests.integration.infrastructure.opensearch_index_resource import OpensearchIndexResource


class MainStack(TestingStack):
    OPENSEARCH_DOMAIN_ENDPOINT = 'OpensearchDomainEndpoint'
    INDEX_NAME = 'OpensearchIndexName'
    FUNCTION1_NAME = 'Function1name'

    def __init__(self, scope: Construct) -> None:
        super().__init__(scope=scope)

        opensearch = OpensearchDomainStack(
            scope=self
        )

        prefix = TestingStack.global_prefix()
        index_stack_name = f'{prefix}OpensearchIndexStack'
        index_stack = Stack(
            scope=scope,
            id=index_stack_name,
            stack_name=index_stack_name
        )
        index = OpensearchIndexResource(
            scope=index_stack,
            opensearch_domain=opensearch.domain.domain_endpoint
        )

        function1 = Function1(scope=self)

        self.add_output(key=self.OPENSEARCH_DOMAIN_ENDPOINT, value=opensearch.domain.domain_endpoint)
        self.add_output(key=self.INDEX_NAME, value=index.index_name)
        self.add_output(key=self.FUNCTION1_NAME, value=function1.function_name)
