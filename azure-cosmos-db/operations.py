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


def create_client(config):
    server_url = config.get('server_url')
    api_key = config.get('api_key')
    database_name = config.get('database_name')
    collection_name = config.get('collection_name')

    client = CosmosClient("{url}".format(url=server_url), credential="{api_key}".format(api_key=api_key))
    database = client.get_database_client(database_name)
    container = database.get_container_client(collection_name)
    return database, container


def check_health(config):
    try:
        if get_collections(config, params={}):
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
        database, container = create_client(config)
        create_item = container.upsert_item(document_details)
        return create_item
    except Exception as Err:
        logger.error('Exception occurred: {}'.format(Err))
        raise ConnectorError(Err)


def query_document(config, params):
    try:
        doc_id = params.get('doc_id')
        collection_name = config.get('collection_name')
        database, container = create_client(config)
        query = "SELECT * FROM {container} r WHERE r.id='{doc_id}'".format(container=collection_name, doc_id=doc_id)
        for item in container.query_items(
                query='SELECT * FROM {container} r WHERE r.id="{doc_id}"'.format(container=collection_name,
                                                                                  doc_id=doc_id),
                enable_cross_partition_query=True):
            return item
    except Exception as Err:
        logger.error('Exception occurred: {}'.format(Err))
        raise ConnectorError(Err)


def update_document(config, params):
    try:
        doc_id = params.get('doc_id')
        document_details = params.get('document_details')
        database, container = create_client(config)
        document_details.update({"id": doc_id})
        update_item = container.upsert_item(document_details)
        return update_item
    except Exception as Err:
        logger.error('Exception occurred: {}'.format(Err))
        raise ConnectorError(Err)


def get_collections(config, params):
    try:
        database, container = create_client(config)
        collections_list = []
        for item in database.list_containers():
            collections_list.append(item)
        return collections_list
    except Exception as Err:
        logger.error('Exception occurred: {}'.format(Err))
        raise ConnectorError(Err)


def get_database_properties(config, params):
    try:
        database, container = create_client(config)
        properties = database.read()
        return properties
    except Exception as Err:
        logger.error('Exception occurred: {}'.format(Err))
        raise ConnectorError(Err)


operations = {'insert_document': insert_document,
              'query_document': query_document,
              'update_document': update_document,
              'get_collections': get_collections,
              'get_database_properties': get_database_properties
              }
