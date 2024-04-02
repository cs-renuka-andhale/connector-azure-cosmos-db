"""
Copyright start
MIT License
Copyright (c) 2024 Fortinet Inc
Copyright end
"""

import time
from azure.cosmos import CosmosClient

from connectors.core.connector import get_logger, ConnectorError
from connectors.core.connector import Connector

logger = get_logger('azure-cosmos-db')


def create_client(config, params):
    server_url = config.get('server_url')
    if not (server_url.startswith('https://') or server_url.startswith('http://')):
        server_url = 'https://' + server_url
    api_key = config.get('api_key')
    database_name = config.get('database_name') 
    if params.get('database_name'):
        database_name = params.get('database_name')

    client = CosmosClient("{url}".format(url=server_url), credential="{api_key}".format(api_key=api_key))
    database = client.get_database_client(database_name)
    return database


def check_health(config):
    try:
        if get_database_properties(config, params={}):
            return True
        else:
            logger.exception('Error occured while connecting server')
            raise ConnectorError('Error occured while connecting server')
    except Exception as Err:
        logger.exception('Error occured while connecting server: {}'.format(str(Err)))
        raise ConnectorError('Error occured while connecting server: {}'.format(Err))


def insert_document(config, params):
    try:
        document_details = params.get('document_details')
        database = create_client(config, params)
        container = database.get_container_client(params.get('collection_name'))
        create_item = container.upsert_item(document_details)
        return create_item
    except Exception as Err:
        logger.error('Exception occurred: {}'.format(Err))
        raise ConnectorError(Err)


def query_document(config, params):
    try:
        doc_id = params.get('doc_id')
        collection_name = params.get('collection_name')
        query = params.get('query')
        item_list = []
        database = create_client(config, params)
        container = database.get_container_client(params.get('collection_name'))
        for item in container.query_items(query, enable_cross_partition_query=True):
            item_list.append(item) 
        return item_list
    except Exception as Err:
        logger.error('Exception occurred: {}'.format(Err))
        raise ConnectorError(Err)


def update_document(config, params):
    try:
        doc_id = params.get('doc_id')
        document_details = params.get('document_details')
        database = create_client(config, params)
        container = database.get_container_client(params.get('collection_name'))
        document_details.update({"id": doc_id})
        update_item = container.upsert_item(document_details)
        return update_item
    except Exception as Err:
        logger.error('Exception occurred: {}'.format(Err))
        raise ConnectorError(Err)


def delete_document(config, params):
    try:
        doc_id = params.get('doc_id')
        partition_key = params.get('partition_key')
        database = create_client(config, params)
        container = database.get_container_client(params.get('collection_name'))
        delete_item = container.delete_item(doc_id, partition_key=partition_key)
        if delete_item == None:
            return "Document: {doc_id} deleted successfully".format(doc_id=doc_id)
        return delete_item

        # for item in container.query_items(
        #         query='SELECT * FROM {container} r WHERE r.id="{doc_id}"'.format(container=collection_name,
        #                                                                          doc_id=doc_id),
        #         enable_cross_partition_query=True):
        #     delete_item = container.delete_item(item, partition_key=partition_key)
        #     return delete_item

    except Exception as Err:
        logger.error('Exception occurred: {}'.format(Err))
        raise ConnectorError(Err)


def get_collections(config, params):
    try:
        database = create_client(config, params)
        collections_list = []
        for item in database.list_containers():
            collections_list.append(item)
        return collections_list
    except Exception as Err:
        logger.error('Exception occurred: {}'.format(Err))
        raise ConnectorError(Err)


def get_database_properties(config, params):
    try:
        database = create_client(config, params)
        properties = database.read()
        return properties
    except Exception as Err:
        if 'Resource Not Found' in str(Err):
            raise ConnectorError("Resource Not Found")
        else:
            logger.error('Exception occurred: {}'.format(Err))
            raise ConnectorError(Err)


operations = {'insert_document': insert_document,
              'query_document': query_document,
              'update_document': update_document,
              'delete_document': delete_document,
              'get_collections': get_collections,
              'get_database_properties': get_database_properties
              }
