from aws_cdk.core import App

from b_cfn_opensearch_index_tests.integration.infrastructure.main_stack import MainStack

# Initiate CDK applications and synthesize it.
app = App()
MainStack(app)
app.synth()
