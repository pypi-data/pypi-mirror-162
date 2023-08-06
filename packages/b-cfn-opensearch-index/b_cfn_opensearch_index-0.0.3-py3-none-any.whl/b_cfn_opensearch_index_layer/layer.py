from importlib.metadata import version
from typing import List, Optional

from aws_cdk.aws_lambda import Runtime
from aws_cdk.core import Stack
from b_cfn_lambda_layer.lambda_layer import LambdaLayer, PackageVersion


class OpensearchIndexLayer(LambdaLayer):
    DEPENDENCIES = [
        'b-aws-cf-response',
        'opensearch-py',
        'requests-aws4auth',
    ]

    def __init__(
            self,
            scope: Stack,
            name: str
    ) -> None:
        super().__init__(
            scope=scope,
            name=name,
            source_path=self.source_path(),
            code_runtimes=self.runtimes(),
            additional_pip_install_args='--use-deprecated=legacy-resolver',
            dependencies={
                dependency_name: PackageVersion.from_string_version(version(dependency_name))
                for dependency_name in self.DEPENDENCIES
            }

        )

    @staticmethod
    def source_path() -> str:
        from . import root
        return root

    @staticmethod
    def runtimes() -> Optional[List[Runtime]]:
        return [Runtime.PYTHON_3_8]
