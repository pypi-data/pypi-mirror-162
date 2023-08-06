from aws_cdk.aws_ec2 import EbsDeviceVolumeType
from aws_cdk.aws_iam import AccountRootPrincipal, Effect, PolicyStatement
from aws_cdk.aws_opensearchservice import (
    CapacityConfig,
    Domain,
    EbsOptions,
    EngineVersion,
    ZoneAwarenessConfig
)
from aws_cdk.core import RemovalPolicy, Stack
from b_aws_testing_framework.tools.cdk_testing.testing_stack import TestingStack


class OpensearchDomainStack(Stack):
    def __init__(self, scope: Stack) -> None:
        super().__init__(scope=scope, id='OpensearchDomainStack')

        prefix = TestingStack.global_prefix()

        capacity_config = CapacityConfig(
            data_node_instance_type='t3.small.search',
            data_nodes=1,
            master_nodes=None,
        )

        ebs_options = EbsOptions(
            enabled=True,
            volume_size=10,
            volume_type=EbsDeviceVolumeType.GP2
        )

        self.domain = Domain(
            scope=self,
            id=f'{prefix}OpensearchDomain',
            domain_name=f'{prefix}-opensearch'.lower(),
            version=EngineVersion.OPENSEARCH_1_0,
            access_policies=[
                PolicyStatement(
                    actions=['es:*'],
                    effect=Effect.ALLOW,
                    resources=['*'],
                    principals=[AccountRootPrincipal()],
                ),
            ],
            capacity=capacity_config,
            ebs=ebs_options,
            removal_policy=RemovalPolicy.DESTROY,
            zone_awareness=ZoneAwarenessConfig(enabled=False)
        )
