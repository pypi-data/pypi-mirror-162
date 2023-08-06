from aws_cdk.core import Stack

from b_aws_testing_framework.tools.cdk_testing.testing_stack import TestingStack
from b_cfn_opensearch_index.resource import OpensearchIndex
from b_cfn_opensearch_index_tests.integration.tests.dummy_index import dummy_index


class OpensearchIndexResource(OpensearchIndex):
    def __init__(self, scope: Stack, opensearch_domain: str) -> None:
        prefix = TestingStack.global_prefix()
        super().__init__(
            scope=scope,
            name=f'{prefix}IndexCreate',
            opensearch_domain_endpoint=opensearch_domain,
            index_prefix=dummy_index['index_prefix'],
            index_settings=dummy_index['index_settings'],
            index_mapping_settings=dummy_index['index_mappings'],
            reindex=True
        )
