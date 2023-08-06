from aws_cdk.aws_iam import Effect, PolicyStatement
from aws_cdk.aws_lambda import Code, Function, Runtime
from aws_cdk.core import Stack
from b_aws_testing_framework.tools.cdk_testing.testing_stack import TestingStack

from b_cfn_opensearch_index_layer.layer import OpensearchIndexLayer
from .source import root


class Function1(Function):
    """
    Function that allows us to test OpensearchIndexLayer and its functionality.
    """

    def __init__(self, scope: Stack):

        super().__init__(
            scope=scope,
            id=f'{TestingStack.global_prefix()}TestingFunction1',
            code=Code.from_asset(root),
            handler='index.handler',
            runtime=Runtime.PYTHON_3_8,
            layers=[
                OpensearchIndexLayer(
                    scope=scope,
                    name=f'{TestingStack.global_prefix()}TestFunction1Layer'
                )
            ]
        )

        self.add_to_role_policy(
            PolicyStatement(
                actions=['es:*'],
                resources=['*'],
                effect=Effect.ALLOW
            )
        )
