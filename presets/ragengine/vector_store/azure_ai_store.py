# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import logging
from typing import List, Dict
import os
from ragengine.models import Document
from ragengine.embedding.base import BaseEmbeddingModel

import pymongo
import json
from llama_index.core import (VectorStoreIndex)
from llama_index.vector_stores.azureaisearch import (
    AzureAISearchVectorStore,
    IndexManagement,
    MetadataIndexFieldType,
)
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.aio import (
    SearchIndexClient as AsyncSearchIndexClient,
)

from .base import BaseVectorStore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureAIIndexSpec:
    def __init__(self, index_name: str, id_field_key: str, chunk_field_key: str,
                 embedding_field_key: str, embedding_dimensionality: int,
                 doc_id_field_key: str, language_analyzer: str,
                 vector_algorithm_type: str, metadata_fields: Dict[str, MetadataIndexFieldType],
                 semantic_configuration_name: str):
        self.index_name = index_name
        self.metadata_fields = metadata_fields
        self.id_field_key = id_field_key
        self.chunk_field_key = chunk_field_key
        self.embedding_field_key = embedding_field_key
        self.embedding_dimensionality = embedding_dimensionality
        self.doc_id_field_key = doc_id_field_key
        self.language_analyzer = language_analyzer
        self.vector_algorithm_type = vector_algorithm_type
        self.semantic_configuration_name = semantic_configuration_name
    
    def __str__(self):
        return f"AzureAIIndexSpec(index_name={self.index_name}, id_field_key={self.id_field_key}, chunk_field_key={self.chunk_field_key}, embedding_field_key={self.embedding_field_key}, embedding_dimensionality={self.embedding_dimensionality}, doc_id_field_key={self.doc_id_field_key}, language_analyzer={self.language_analyzer}, vector_algorithm_type={self.vector_algorithm_type}, semantic_configuration_name={self.semantic_configuration_name})"
    
def index_from_dict(data: Dict) -> AzureAIIndexSpec:
    return AzureAIIndexSpec(
        index_name=data["name"],
        id_field_key=data.get("idField", "chunk_id"),
        chunk_field_key=data.get("chunkField", "chunk"),
        embedding_field_key=data.get("embeddingField", "embedding"),
        embedding_dimensionality=data.get("dimensions", 1536),
        doc_id_field_key=data.get("documentIdField", "parent_id"),
        language_analyzer=data.get("languageAnalyzer", "en.lucene"),
        vector_algorithm_type=data.get("vectorAlgorithm", "exhaustiveKnn"),
        semantic_configuration_name=data.get("semanticConfigurationName", "mySemanticConfig"),
        metadata_fields=data.get("metadataField", {}),
    )

class AzureAISearchVectorStoreHandler(BaseVectorStore):
    def __init__(self, embedding_manager):
        super().__init__(embedding_manager)
        self.service_key = os.getenv("AZURE_AI_SEARCH_SERVICE_KEY")
        self.connection_string = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.dimension = self.embed_model.get_embedding_dimension()
        try:
            self.index_client = SearchIndexClient(
                endpoint=self.connection_string,
                credential=AzureKeyCredential(self.service_key),
            )
            self.async_index_client = AsyncSearchIndexClient(
                endpoint=self.connection_string,
                credential=AzureKeyCredential(self.service_key),
            )
        except Exception as e:
            raise Exception(f"Failed to create search client: {e}")

    def load_preset_indexes(self):
        index_definitions = os.getenv("INDEX_DEFINTIONS")
        if index_definitions:
            print(f"Loading index definitions from environment variable: {index_definitions}")
            for index_definition in json.loads(index_definitions):
                print(f"Creating index: {index_definition}")
                index_spec = index_from_dict(data=index_definition)
                self.load_index(azure_search_index_spec=index_spec)
        else:
            raise ValueError("INDEX_DEFINTIONS environment variable not set.")

    def _create_new_index(self, index_name: str, documents: List[Document]) -> List[str]:
        metadata_fields = {}
        vector_store = AzureAISearchVectorStore(
            search_or_index_client=self.index_client,
            # filterable_metadata_field_keys=metadata_fields,
            hidden_field_keys=["text_vector"],
            index_name=index_name,
            index_management=IndexManagement.CREATE_IF_NOT_EXISTS,
            id_field_key="chunk_id",
            chunk_field_key="chunk",
            embedding_field_key="text_vector",
            embedding_dimensionality=1536,
            metadata_string_field_key="metadata",
            doc_id_field_key="parent_id",
            language_analyzer="en.lucene",
            vector_algorithm_type="exhaustiveKnn",
            semantic_configuration_name="mySemanticConfig",
        )
        return self._create_index_common(index_name, documents, vector_store)
    
    def load_index(self, azure_search_index_spec: AzureAIIndexSpec) -> str:
        try:
            print(azure_search_index_spec)
            metadata_fields = {}
            vector_store = AzureAISearchVectorStore(
                search_or_index_client=self.index_client,
                async_search_or_index_client=self.async_index_client,
                # filterable_metadata_field_keys=metadata_fields,
                hidden_field_keys=[azure_search_index_spec.embedding_field_key],
                index_name=azure_search_index_spec.index_name,
                index_management=IndexManagement.CREATE_IF_NOT_EXISTS,
                id_field_key=azure_search_index_spec.id_field_key,
                chunk_field_key=azure_search_index_spec.chunk_field_key,
                embedding_field_key=azure_search_index_spec.embedding_field_key,
                embedding_dimensionality=azure_search_index_spec.embedding_dimensionality,
                metadata_string_field_key="metadata",
                doc_id_field_key=azure_search_index_spec.doc_id_field_key,
                language_analyzer=azure_search_index_spec.language_analyzer,
                vector_algorithm_type=azure_search_index_spec.vector_algorithm_type,
                semantic_configuration_name=azure_search_index_spec.semantic_configuration_name,
            )

            index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                embed_model=self.embed_model,
            )
            index.set_index_id(azure_search_index_spec.index_name)
            self.index_map[azure_search_index_spec.index_name] = index
            self.index_store.add_index_struct(index.index_struct)
            
            print(f"Loaded index {self.index_map}")

            return azure_search_index_spec.index_name
        except Exception as e:
            logger.error(f"Failed to load index {azure_search_index_spec.index_name}: {e}")
            raise e