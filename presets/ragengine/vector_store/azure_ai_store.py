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

    async def _create_new_index(self, index_name: str, documents: List[Document]) -> List[str]:
        vector_store = AzureAISearchVectorStore(
            search_or_index_client=self.index_client,
            async_search_or_index_client=self.async_index_client,
            # filterable_metadata_field_keys=metadata_fields,
            hidden_field_keys=["text_vector"],
            index_name=index_name,
            index_management=IndexManagement.CREATE_IF_NOT_EXISTS,
            id_field_key="chunk_id",
            chunk_field_key="chunk",
            embedding_field_key="text_vector",
            embedding_dimensionality=self.dimension,
            metadata_string_field_key="metadata",
            doc_id_field_key="parent_id",
            language_analyzer="en.lucene",
            vector_algorithm_type="exhaustiveKnn",
            semantic_configuration_name="mySemanticConfig",
        )
        return await self._create_index_common(index_name, documents, vector_store)
