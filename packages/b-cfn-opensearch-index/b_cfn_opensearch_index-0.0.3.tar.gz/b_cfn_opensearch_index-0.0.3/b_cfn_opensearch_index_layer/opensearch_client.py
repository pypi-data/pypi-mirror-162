from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, OpenSearchException
from opensearchpy.helpers import bulk
from requests_aws4auth import AWS4Auth


class OpensearchClient(OpenSearch):
    def __init__(
        self,
        boto3_session: boto3.Session,
        opensearch_endpoint: str
    ) -> None:

        credentials = boto3_session.get_credentials()
        aws_auth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            boto3_session.region_name,
            'es',
            session_token=credentials.token
        )
        super().__init__(
            hosts=[{'host': opensearch_endpoint, 'port': 443}],
            http_auth=aws_auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )

    def bulk_action(
        self,
        actions: Iterable,
        stats_only: Optional[bool] = True,
        raise_on_error: Optional[bool] = False,
        raise_on_exception: Optional[bool] = False,
    ) -> Tuple[int, Union[int, List[Dict[str, Any]]]]:
        """
        The wrapper of the method opensearchpy.helpers.bulk.
        Uses actions iterator to send chunks of data to Opensearch for updating indexes.

        :param actions: Iterator containing the dictionary that represents data item for indexing.
        :param stats_only: If True only a report of success/failed operations will be returned instead of 
                the number of successes and a list of error responses. Default: True.
        :param raise_on_error: If True BulkIndexError can be raised from indexing of last data chunk. 
                Default: False.
        :param raise_on_exception: If True exceptions will be propagated from call to bulk instead of 
                reporting items that failed as failed. Default: False.

        :return: A quantified information of successfully processed and failed items. In case stats_only 
                parameter set to False method will return a quantity of successfully processed items and a 
                list of failed items. 
        """

        success, fails = bulk(
            self,
            actions,
            stats_only=stats_only,
            raise_on_error=raise_on_error,
            raise_on_exception=raise_on_exception
        )

        return success, fails

    def search_documents(self, query: Dict[str, Any], index_name: str) -> List[Dict[str, Any]]:
        """
        Search for documents by given query and index name.

        :param query: Dictionary representation of OpenSearch query.
        :param index_name: A name of index to query. 

        :return: A list of query results in a dictionary format.
        """

        try:
            response = self.search(
                index=index_name,
                body=query
            )
        except OpenSearchException as ex:
            raise Exception(f'Could not query Opensearch. Reason: {repr(ex)}.')

        return [result['_source'] for result in response['hits']['hits']]
