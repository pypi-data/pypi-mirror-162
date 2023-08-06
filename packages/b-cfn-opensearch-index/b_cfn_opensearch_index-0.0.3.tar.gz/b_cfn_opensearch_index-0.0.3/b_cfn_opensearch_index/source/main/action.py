import json
import logging
from secrets import token_urlsafe
from typing import Any, Dict, NamedTuple, Optional

import boto3
from b_cfn_opensearch_index_layer.opensearch_client import OpensearchClient

from .opensearch_index_id import OpensearchIndexId

logger = logging.getLogger()


class ActionResult(NamedTuple):
    """
    Custom data to return back to CloudFormation service, physical resource id (can be empty).
    """

    data: Optional[Dict[Any, Any]]
    resource_id: str = None


class Actions:
    def __init__(self, invocation_event: Dict[str, Any]) -> None:
        """
        Executes custom resource request event. 

        Method create - creates an empty index at designated OpenSearch endpoint using defined 
            index settings and index mappings.
        Method update - updates dynamic settings and mappings of the existing index. In case of index name change 
            update action creates a new index using defined index settings and mappings and reindexes documents using 
            a newly created index. Reindex option can be switched off explicitly setting ResourceProperties Reindex 
            value to False.
        Method delete - removes index from designated OpenSearch endpoint. All indexed documents are wiped too. 

        :param invocation_event: Event message of custom resource invocation.
        Example of the AWS custom resource invocation event message:

            'RequestType' : 'Create',
            'ResponseURL' : 'http://pre-signed-S3-url-for-response',
            'StackId' : 'arn:aws:cloudformation:eu-central-1:123456789012:stack/stack-name/guid',
            'RequestId' : 'unique id for this create request',
            'ResourceType' : 'Custom::OpensearchIndex',
            'LogicalResourceId' : 'CustomResourceIndexCreate,
            'ResourceProperties' : {
                'OpensearchDomainEndpoint' : 'opensearch.eu-central-1.es.amazonaws.com'
                'IndexSettings': {
                    'index.refresh_interval': '2s'
                },
                'IndexPrefix': 'some-index',
                'Redindex': 'true',
                'IndexMappingSettings' : {
                    'author': {
                        'type': 'keyword'
                    } 
                }
            }

        RequestType - determines what action should be performed.
        ResponseURL - Presigned S3 URL where the response should be sent to.
        ResourceProperties - Custom payload from AWS CloudFormation. Includes necessary information for the creation 
            of the custom resource.
        """

        self.__properties: Dict[str, Any] = invocation_event['ResourceProperties']
        self.__old_properties: Optional[Dict[str, Any]] = invocation_event.get('OldResourceProperties')
        self.__resource_id: Optional[str] = invocation_event.get('PhysicalResourceId')

        self.index_prefix = self.__properties['IndexPrefix']

        self.opensearch_domain_endpoint = self.__properties['OpensearchDomainEndpoint']
        self.index_settings = self.__properties.get('IndexSettings') or {}
        self.index_mapping_settings = {
            'properties': self.__properties.get('IndexMappingSettings') or {}
        }

        # Setup Opensearch client.
        self.opensearch_client = OpensearchClient(
            boto3_session=boto3.Session(),
            opensearch_endpoint=self.opensearch_domain_endpoint
        )

    def create(self) -> ActionResult:
        """
        Creates an empty index applying index settings and mappings from invocation event Resource Properties.

        :return: Create action result.
        """

        logger.info(f'Initiating resource creation with these properties: {json.dumps(self.__properties)}.')

        # Create index name by concatenating index prefix and url safe random string.
        index_name = f'{self.index_prefix}-{token_urlsafe(8)}'.lower()

        self.__create(
            index_name=index_name,
            body={
                'settings': self.index_settings,
                'mappings': self.index_mapping_settings
            }
        )

        return ActionResult(
            data={'IndexName': index_name},
            resource_id=OpensearchIndexId(
                opensearch_endpoint=self.opensearch_domain_endpoint,
                index_name=index_name
            ).make_resource_id()
        )

    def update(self):
        """
        Update settings and mapping of existing index.

        Only dynamic index settings can be updated. On try to update static index settings an exception will be raised.

        :return: Update action result.
        """

        logger.info(f'Initiating resource update with these properties: {json.dumps(self.__properties)}.')

        # Extracing index name from PhysicalResourceId.
        index_name = OpensearchIndexId.resource_id(resource_id=self.__resource_id).index_name
        # Extracting old index prefix from custom resource old properties.
        old_index_prefix = self.__old_properties['IndexPrefix']

        # In case new index prefix diffears old one create new index with new name. Index name cannot be updated.
        # CloudFormation will delete old index together with all documents which were indexed using this index.
        if self.index_prefix != old_index_prefix:
            new_index_name = f'{self.index_prefix}-{token_urlsafe(8)}'.lower()
            self.__create(
                index_name=new_index_name,
                body={
                    'settings': self.index_settings,
                    'mappings': self.index_mapping_settings
                }
            )
            # Try to reindex existing documents using new index.
            if self.__properties['Reindex']:
                self.__reindex(
                    source_index_name=index_name,
                    target_index_name=new_index_name
                )

            return ActionResult(
                data={'IndexName': new_index_name},
                resource_id=OpensearchIndexId(
                    opensearch_endpoint=self.opensearch_domain_endpoint,
                    index_name=new_index_name
                ).make_resource_id()
            )
        else:
            # Update settings and mapping of the index.
            self.__update(index_name=index_name)

            return ActionResult(data={'IndexName': index_name}, resource_id=self.__resource_id)

    def delete(self) -> ActionResult:
        """
        Deletes an Opensearch index with index name which is parsed from PhysicalResourceId.

        :return: Delete action result.
        """

        logger.info(f'Initiating resource delete with these properties: {json.dumps(self.__properties)}.')

        index_name = OpensearchIndexId.resource_id(resource_id=self.__resource_id).index_name

        self.opensearch_client.indices.delete(
            index=index_name,
            expand_wildcards='all'
        )
        return ActionResult(data={'IndexName': index_name}, resource_id=self.__resource_id)

    def __create(self, index_name: str, body: Dict[str, Any]) -> None:
        """
        Posting index create request to Opensearch endpoint.

        :param index_name: Name of the new index.
        :parm body: Query of Opensearch index create request.
                    e.g. {
                        'settings': {
                            'refresh_interval': '2s'
                        },
                        'mappings': {
                            'properties': {
                                'id': 'keyword',
                                'author': 'keyword'
                                'title': 'keyword',
                                'content': 'text'
                            }
                        }
                    }

        :return: None.
        """

        try:
            self.opensearch_client.indices.create(
                index=index_name,
                body=body,
            )
        except Exception as ex:
            raise Exception(f'Index creation failed. Reason: {repr(ex)}.')

    def __update(self, index_name: str) -> None:
        """
        Update dynamic settings and mappings of the existing index.

        Skipping update and raise an exception in case index settings in ResourceProperties contains static index settings.
        Static index settings cannot be updated, they can be set only at the moment of index creation. 

        :return: No return.
        """

        # List of static index settings. These settings cannot be updated on live index.
        # https://opensearch.org/docs/latest/opensearch/rest-api/index-apis/create-index/
        static_index_settings = [
            'index.number_of_shards',
            'index.number_of_routing_shards',
            'index.shard.check_on_startup',
            'index.codec',
            'index.routing_partition_size'
            'index.soft_deletes.retention_lease.period',
            'index.load_fixed_bitset_filters_eagerly',
            'index.hidden'
        ]

        # Check does requested index settings update holds any of static index settings.
        if any(key in self.index_settings for key in static_index_settings):
            raise Exception(
                f'Failed to update settings of the live index. '
                f'Reason: Static index settings cannot be updated. {static_index_settings=}'
            )

        try:
            # Update dynamic index settings.
            self.opensearch_client.indices.put_settings(
                index=index_name,
                body=self.index_settings,
                timeout='5m'
            )
        except Exception as ex:
            raise Exception(f'Failed to update settings of the live index. Reason: {repr(ex)}.')

        try:
            # Update index mappings.
            self.opensearch_client.indices.put_mapping(
                index=index_name,
                body=self.index_mapping_settings,
                timeout='5m'
            )
        except Exception as ex:
            raise Exception(f'Failed to update mappings of the live index. Reason: {repr(ex)}.')

    def __reindex(self, source_index_name: str, target_index_name: str) -> None:
        """
        Migrates documents from source index to target index.

        Slices parameter of reindex set to auto what allows OpenSearch choose the optimal number of slices to use.
        Slicing of reindex task - splits reindex task into smaller ones and executes them in parallel.

        :return: No return.
        """

        try:
            self.opensearch_client.reindex(
                body={
                    'source': {
                        'index': source_index_name,
                    },
                    'dest': {
                        'index': target_index_name
                    }
                },
                refresh=True,
                slices='auto',
                timeout='10m'
            )
        except Exception as ex:
            logger.warning(f'Failed to reindex documents. Reason: {repr(ex)}.')
