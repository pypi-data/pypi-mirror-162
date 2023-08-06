from functools import lru_cache
from typing import List

from aws_cdk.aws_iam import Effect, PolicyStatement
from aws_cdk.aws_lambda import Code, Runtime, SingletonFunction
from aws_cdk.core import Duration, Stack
from b_cfn_lambda_layer.lambda_layer import LambdaLayer


class OpensearchIndexFunction(SingletonFunction):
    def __init__(self, scope: Stack, name: str, layers: List[LambdaLayer]) -> None:
        self.__name = name
        super().__init__(
            scope=scope,
            id=name,
            uuid='OpensearchIndex',
            code=self.__code(),
            handler='main.index.handler',
            runtime=Runtime.PYTHON_3_8,
            function_name=name,
            layers=layers,
            timeout=Duration.minutes(15),
        )

        self.add_to_role_policy(
            PolicyStatement(
                actions=['es:*'],
                resources=['*'],
                effect=Effect.ALLOW
            )
        )

    @lru_cache
    def __code(self) -> Code:
        from .source import root
        return Code.from_asset(root)

    @property
    def function_name(self):
        return self.__name
