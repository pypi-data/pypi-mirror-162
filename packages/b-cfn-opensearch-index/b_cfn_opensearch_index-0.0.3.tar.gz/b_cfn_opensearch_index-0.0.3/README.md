# B.CfnOpenSearchIndex

**b-cfn-opensearch-index** - AWS CloudFormation custom resource that handles the creation, update and removals of OpenSearch indexes.

### Description

While you can create an OpenSearch index just by using a document as a base, using this AWS CDK resource lets you create an empty index for later use.<br>
The resource supports **update** action, however, there are some limitations (please refer to "Known limits").<br>Update action triggers reindexing of documents by default to prevent data loss.<br>
The resource also supports **delete** action, where removal of created index removes all previously created indexes.<br>**Attention** removal of indexes destroys all indexed documents.

### Remarks

[Biomapas](https://biomapas.com) aims to modernise life-science
industry by sharing its IT knowledge with other companies and
the community.

### Related technology

- Python 3.8
- OpenSearch
- Amazon Web Services (AWS)
- AWS CloudFormation
- AWS Cloud Development Kit (CDK)

### Assumptions

- You have basic-good knowledge in python programming.
- You have basic-good knowledge in AWS and CloudFormation.
- You have basic-good knowledge in OpenSearch.

### Useful sources

- Read more about Cloud Formation: https://docs.aws.amazon.com/cloudformation/index.html
- Read more about Opensearch: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/remote-reindex.html

### Install

Use the package manager pip to install this package. This project is not in the PyPi
repository yet. Install directly from source or PyPI.

```bash
pip install .
```

Or

```bash
pip install b-cfn-opensearch-index
```

### Usage & Examples

Usage of this AWS CloudFormation custom resource is quite simple. Initialize it within any valid CDK scope giving a unique name, OpenSearch domain endpoint, index name prefix, and settings/mappings of the index.

Bellow is an example:

```python
from aws_cdk.core import Stack

from b_cfn_opensearch_index.resource import OpensearchIndex


class ExampleOpensearchIndexStack(Stack):
    def __init__(self, scope: Stack, opensearch_domain_endpoint: str) -> None:
        super().__init__(scope=scope, id='ExampleOpensearchIndexStack')

        # Define index settings.
        index_settings = {
             'index.refresh_interval': '2s',
        }

        # Define index mappings.
        index_mappings = {
            'id': {
                'type': 'keyword'
            },
            'author': {
                'type': 'keyword'
            },
            'title': {
                'type': 'keyword'
            },
            'content': {
                'type': 'text'
            },
            'timestamp': {
                'type': 'date',
                'format': 'yyyy-MM-dd HH:mm:ss||epoch_millis'
            },
        }

        # Initialize AWS CloudFormation custom resource using given OpenSearch
        # domain endpoint with defined settings and mappings of the index.
        self.index = OpensearchIndex(
            scope=self,
            name='OpensearchIndex',
            opensearch_domain_endpoint=opensearch_domain_endpoint,
            index_prefix='example-index-prefix',
            index_settings=index_settings
            index_mapping_settings=index_mappings
        )

```

In the example above, we created an OpenSearch index with two dictionaries for settings and mappings of the index. More information about settings and mappings of the index can be found here https://opensearch.org/docs/latest/opensearch/rest-api/index-apis/create-index/.

Index prefix can be any string that complies with index naming restrictions listed in section **Known limits**.

On change of index name (index prefix), reindex of all documents will be triggered. If there is a need to skip reindex of the documents please set **`reindex`** parameter with the value **`False`**.

```python

self.index = OpensearchIndex(
    scope=self,
    name='OpensearchIndex',
    opensearch_domain_endpoint=opensearch_domain_endpoint,
    index_prefix='example-index-prefix',
    index_settings=index_settings
    index_mapping_settings=index_mappings,
    reindex=False
)
```

Following parameters are optional and can be omitted:

- `index_settings`
- `index_mappings`
- `reindex`

### Known limits

There are some limitations. Currently, reindex of documents is not possible if the OpenSearch domain endpoint changes.<br><br>
Update settings and mappings of the index have some limitations too:<br>

- Update of static index settings is not possible. Static index settings can be set only at the moment of index creation.<br>
- Change of index mappings field types is not possible. Setup of field types only at the moment of index creation. To bypass this limitation, trigger index update by changing index name with new index mappings. (example at Usage & Examples).<br>
- There are some index naming restrictions. Keep in mind those restriction at the moment of index prefix setup.<br>
  - Index names can’t begin with underscores (\_) or hyphens (-).
  - Index names can’t contain spaces, commas, or the following characters: <br>
    ```
    :, ", *, +, /, \, |, ?, #, >, or <
    ```

### Testing

This project has integration tests based on pytest. To run tests, simply run:

```
pytest
```

### Contribution

Found a bug? Want to add or suggest a new feature?<br>
Contributions of any kind are gladly welcome. You may contact us
directly, create a pull-request or an issue in github platform.
Lets modernize the world together.
