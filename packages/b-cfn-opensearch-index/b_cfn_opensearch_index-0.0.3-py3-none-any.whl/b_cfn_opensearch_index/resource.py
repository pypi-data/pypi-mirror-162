from typing import Any, Dict, Optional

from aws_cdk.core import CustomResource, RemovalPolicy, Stack

from b_cfn_opensearch_index_layer.layer import OpensearchIndexLayer
from b_cfn_opensearch_index.function import OpensearchIndexFunction


class OpensearchIndex(CustomResource):
    def __init__(
        self,
        scope: Stack,
        name: str,
        opensearch_domain_endpoint: str,
        index_prefix: str,
        index_settings: Optional[Dict[str, Any]] = None,
        index_mapping_settings: Optional[Dict[str, Any]] = None,
        reindex: Optional[bool] = True
    ) -> None:
        layers = [
            OpensearchIndexLayer(
                scope=scope,
                name=f'{name}FunctionLayer'
            ),
        ]

        function = OpensearchIndexFunction(
            scope=scope,
            name=f'{name}Function',
            layers=layers
        )

        super().__init__(
            scope=scope,
            id=f'CustomResource{name}',
            service_token=function.function_arn,
            removal_policy=RemovalPolicy.DESTROY,
            resource_type='Custom::OpensearchIndex',
            properties={
                'OpensearchDomainEndpoint': opensearch_domain_endpoint,
                'IndexPrefix': index_prefix,
                'IndexSettings': index_settings,
                'IndexMappingSettings': index_mapping_settings,
                'Reindex': reindex
            }
        )

    @property
    def index_name(self):
        return self.get_att_string('IndexName')
