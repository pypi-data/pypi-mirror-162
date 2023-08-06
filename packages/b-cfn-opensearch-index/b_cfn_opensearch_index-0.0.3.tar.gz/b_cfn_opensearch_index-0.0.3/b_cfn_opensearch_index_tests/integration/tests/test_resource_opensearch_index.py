from time import sleep
from typing import Callable

import pytest

from b_cfn_opensearch_index_tests.integration.infrastructure.main_stack import MainStack
from b_cfn_opensearch_index_tests.integration.tests.dummy_index import dummy_index


@pytest.mark.skip()
def test_RESOURCE_index_WITH_deployed_dummy_index_EXPECT_index_created_successfully(
        opensearch_client: Callable
) -> None:
    """
    Check does custom resource creates a dummy index at the designated OpenSearch endpoint.

    :return: No return.
    """

    index_name = MainStack.get_output(MainStack.INDEX_NAME)
    # Get index from Opensearch by index name.
    index = opensearch_client.indices.get(index=index_name)

    # Make index settings dictionary from received index.
    for key, value in dummy_index['index_settings'].items():
        index_settings = {
            key: value
        }

    # Check does index mappings from Opensearch index match index mappings of dummy_index.
    assert index[index_name]['mappings']['properties'] == dummy_index['index_mappings']
    # Check does index settings from Opensearch index match index settings of dummy_index.
    assert index_settings == dummy_index['index_settings']


@pytest.mark.skip()
def test_RESOURCE_index_WITH_batch_of_documents_EXPECT_documents_found(
        opensearch_client: Callable,
        generate_documents: Callable
) -> None:
    """
    Check OpenSearch index by creating a batch of documents, index them using previously created index. 
    Query OpenSearch for those documents. Check does response of query match documents.

    :return: No return.
    """

    index_name = MainStack.get_output(MainStack.INDEX_NAME)
    # Make a batch of documents and index them with given index.
    documents = generate_documents(index_name)

    # Give some time to index documents.
    sleep(5)

    # Search for documents and compare them with response.
    for document in documents:
        query = {
            'query': {
                'bool': {
                    'must': {
                        'match': {
                            'id': document['id']
                        }
                    }
                }
            }
        }
        response = opensearch_client.search_documents(
            query=query,
            index_name=index_name
        )
        assert document == response[0], response[0]
