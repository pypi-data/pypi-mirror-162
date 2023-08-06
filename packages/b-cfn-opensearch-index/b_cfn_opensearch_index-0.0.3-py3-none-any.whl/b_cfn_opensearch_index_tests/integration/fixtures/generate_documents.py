from typing import Callable, List

import pytest

from .documents import Documents


@pytest.fixture(scope='function')
def generate_documents(faker: Callable, opensearch_client: Callable) -> Callable:
    """
    Fixture giving a function that creates a batch of documents and indexes them using given index name.

    At the end of the test removes created documents from OpenSearch. 

    :return: A function to generate documents and index them at OpenSearch by using given index name.
    """

    batches: List[Documents] = []

    def _generate_document(index_name):
        batch = Documents(faker=faker, index_name=index_name)
        opensearch_client.bulk_action(
            actions=batch.document_action('index')
        )
        batches.append(batch)

        return batch.documents

    yield _generate_document

    for batch in batches:
        opensearch_client.bulk_action(
            actions=batch.document_action('delete')
        )


__all__ = [
    'generate_documents'
]
