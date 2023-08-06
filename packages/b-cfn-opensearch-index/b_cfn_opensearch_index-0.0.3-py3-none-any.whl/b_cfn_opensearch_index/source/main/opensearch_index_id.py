from __future__ import annotations


class OpensearchIndexId:
    """
    Build OpenSearch Index Id using given endpoint and index name or resolve the index name from given resource Id.
    """

    def __init__(self, opensearch_endpoint: str, index_name: str) -> None:
        self.opensearch_endpoint = opensearch_endpoint
        self.index_name = index_name

    def make_resource_id(self):
        """
        Make resource id of OpenSearch index by concatenating given endpoint and index name.
        OpenSearch endpoint and index name concatenated using delimiter '||'.

        :param opensearch_domain: OpenSearch domain endpoint.
        :param index_name: Index name.

        :return: Resource id of OpenSearch index.
        """

        return f'{self.opensearch_endpoint}||{self.index_name}'

    @staticmethod
    def resource_id(resource_id: str) -> OpensearchIndexId:
        """
        Split given resource_id using delimiter '||' and initialize a class.

        :param resource_id: OpenSearch index resource id e.g. opensearch.eu-central-1.es.amazonaws.com||posts-3qs1999pg-c

        :return: OpensearchIndexId class instance.
        """

        return OpensearchIndexId(*resource_id.split('||'))
