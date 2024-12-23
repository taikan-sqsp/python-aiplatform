# -*- coding: utf-8 -*-

# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import re
from typing import Any, Dict, Optional, Sequence, Union
from google.cloud.aiplatform_v1beta1.types import api_auth
from google.cloud.aiplatform_v1beta1 import (
    RagEmbeddingModelConfig as GapicRagEmbeddingModelConfig,
    GoogleDriveSource,
    ImportRagFilesConfig,
    ImportRagFilesRequest,
    RagFileChunkingConfig,
    RagFileParsingConfig,
    RagFileTransformationConfig,
    RagCorpus as GapicRagCorpus,
    RagFile as GapicRagFile,
    SharePointSources as GapicSharePointSources,
    SlackSource as GapicSlackSource,
    JiraSource as GapicJiraSource,
    VertexAiSearchConfig as GapicVertexAiSearchConfig,
    RagVectorDbConfig as GapicRagVectorDbConfig,
)
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.utils import (
    VertexRagDataAsyncClientWithOverride,
    VertexRagDataClientWithOverride,
    VertexRagClientWithOverride,
)
from vertexai.preview.rag.utils.resources import (
    EmbeddingModelConfig,
    VertexPredictionEndpoint,
    LayoutParserConfig,
    LlmParserConfig,
    Pinecone,
    RagCorpus,
    RagFile,
    RagManagedDb,
    SharePointSources,
    SlackChannelsSource,
    TransformationConfig,
    JiraSource,
    VertexAiSearchConfig,
    VertexFeatureStore,
    VertexVectorSearch,
    Weaviate,
    RagVectorDbConfig,
    RagEmbeddingModelConfig,
)


_VALID_RESOURCE_NAME_REGEX = "[a-z][a-zA-Z0-9._-]{0,127}"
_VALID_DOCUMENT_AI_PROCESSOR_NAME_REGEX = (
    r"projects/[^/]+/locations/[^/]+/processors/[^/]+(?:/processorVersions/[^/]+)?"
)


def create_rag_data_service_client():
    return initializer.global_config.create_client(
        client_class=VertexRagDataClientWithOverride,
    ).select_version("v1beta1")


def create_rag_data_service_async_client():
    return initializer.global_config.create_client(
        client_class=VertexRagDataAsyncClientWithOverride,
    ).select_version("v1beta1")


def create_rag_service_client():
    return initializer.global_config.create_client(
        client_class=VertexRagClientWithOverride,
    ).select_version("v1beta1")


def convert_gapic_to_embedding_model_config(
    gapic_embedding_model_config: GapicRagEmbeddingModelConfig,
) -> EmbeddingModelConfig:
    """Convert GapicRagEmbeddingModelConfig to EmbeddingModelConfig."""
    embedding_model_config = EmbeddingModelConfig()
    path = gapic_embedding_model_config.vertex_prediction_endpoint.endpoint
    publisher_model = re.match(
        r"^projects/(?P<project>.+?)/locations/(?P<location>.+?)/publishers/google/models/(?P<model_id>.+?)$",
        path,
    )
    endpoint = re.match(
        r"^projects/(?P<project>.+?)/locations/(?P<location>.+?)/endpoints/(?P<endpoint>.+?)$",
        path,
    )
    if publisher_model:
        embedding_model_config.publisher_model = path
    if endpoint:
        embedding_model_config.endpoint = path
        embedding_model_config.model = (
            gapic_embedding_model_config.vertex_prediction_endpoint.model
        )
        embedding_model_config.model_version_id = (
            gapic_embedding_model_config.vertex_prediction_endpoint.model_version_id
        )

    return embedding_model_config


def _check_weaviate(gapic_vector_db: GapicRagVectorDbConfig) -> bool:
    try:
        return gapic_vector_db.__contains__("weaviate")
    except AttributeError:
        return gapic_vector_db.weaviate.ByteSize() > 0


def _check_rag_managed_db(gapic_vector_db: GapicRagVectorDbConfig) -> bool:
    try:
        return gapic_vector_db.__contains__("rag_managed_db")
    except AttributeError:
        return gapic_vector_db.rag_managed_db.ByteSize() > 0


def _check_vertex_feature_store(gapic_vector_db: GapicRagVectorDbConfig) -> bool:
    try:
        return gapic_vector_db.__contains__("vertex_feature_store")
    except AttributeError:
        return gapic_vector_db.vertex_feature_store.ByteSize() > 0


def _check_pinecone(gapic_vector_db: GapicRagVectorDbConfig) -> bool:
    try:
        return gapic_vector_db.__contains__("pinecone")
    except AttributeError:
        return gapic_vector_db.pinecone.ByteSize() > 0


def _check_vertex_vector_search(gapic_vector_db: GapicRagVectorDbConfig) -> bool:
    try:
        return gapic_vector_db.__contains__("vertex_vector_search")
    except AttributeError:
        return gapic_vector_db.vertex_vector_search.ByteSize() > 0


def _check_rag_embedding_model_config(
    gapic_vector_db: GapicRagVectorDbConfig,
) -> bool:
    try:
        return gapic_vector_db.__contains__("rag_embedding_model_config")
    except AttributeError:
        return gapic_vector_db.rag_embedding_model_config.ByteSize() > 0


def convert_gapic_to_vector_db(
    gapic_vector_db: GapicRagVectorDbConfig,
) -> Union[Weaviate, VertexFeatureStore, VertexVectorSearch, Pinecone, RagManagedDb]:
    """Convert Gapic GapicRagVectorDbConfig to Weaviate, VertexFeatureStore, VertexVectorSearch, RagManagedDb, or Pinecone."""
    if _check_weaviate(gapic_vector_db):
        return Weaviate(
            weaviate_http_endpoint=gapic_vector_db.weaviate.http_endpoint,
            collection_name=gapic_vector_db.weaviate.collection_name,
            api_key=gapic_vector_db.api_auth.api_key_config.api_key_secret_version,
        )
    elif _check_vertex_feature_store(gapic_vector_db):
        return VertexFeatureStore(
            resource_name=gapic_vector_db.vertex_feature_store.feature_view_resource_name,
        )
    elif _check_pinecone(gapic_vector_db):
        return Pinecone(
            index_name=gapic_vector_db.pinecone.index_name,
            api_key=gapic_vector_db.api_auth.api_key_config.api_key_secret_version,
        )
    elif _check_vertex_vector_search(gapic_vector_db):
        return VertexVectorSearch(
            index_endpoint=gapic_vector_db.vertex_vector_search.index_endpoint,
            index=gapic_vector_db.vertex_vector_search.index,
        )
    elif _check_rag_managed_db(gapic_vector_db):
        return RagManagedDb()
    else:
        return None


def convert_gapic_to_vertex_ai_search_config(
    gapic_vertex_ai_search_config: VertexAiSearchConfig,
) -> VertexAiSearchConfig:
    """Convert Gapic VertexAiSearchConfig to VertexAiSearchConfig."""
    if gapic_vertex_ai_search_config.serving_config:
        return VertexAiSearchConfig(
            serving_config=gapic_vertex_ai_search_config.serving_config,
        )
    return None


def convert_gapic_to_rag_embedding_model_config(
    gapic_embedding_model_config: GapicRagEmbeddingModelConfig,
) -> RagEmbeddingModelConfig:
    """Convert GapicRagEmbeddingModelConfig to RagEmbeddingModelConfig."""
    embedding_model_config = RagEmbeddingModelConfig()
    path = gapic_embedding_model_config.vertex_prediction_endpoint.endpoint
    publisher_model = re.match(
        r"^projects/(?P<project>.+?)/locations/(?P<location>.+?)/publishers/google/models/(?P<model_id>.+?)$",
        path,
    )
    endpoint = re.match(
        r"^projects/(?P<project>.+?)/locations/(?P<location>.+?)/endpoints/(?P<endpoint>.+?)$",
        path,
    )
    if publisher_model:
        embedding_model_config.vertex_prediction_endpoint = VertexPredictionEndpoint(
            publisher_model=path
        )
    if endpoint:
        embedding_model_config.vertex_prediction_endpoint = VertexPredictionEndpoint(
            endpoint=path,
            model=gapic_embedding_model_config.vertex_prediction_endpoint.model,
            model_version_id=gapic_embedding_model_config.vertex_prediction_endpoint.model_version_id,
        )
    return embedding_model_config


def convert_gapic_to_backend_config(
    gapic_vector_db: GapicRagVectorDbConfig,
) -> RagVectorDbConfig:
    """Convert Gapic RagVectorDbConfig to VertexVectorSearch, Pinecone, or RagManagedDb."""
    vector_config = RagVectorDbConfig()
    if _check_pinecone(gapic_vector_db):
        vector_config.vector_db = Pinecone(
            index_name=gapic_vector_db.pinecone.index_name,
            api_key=gapic_vector_db.api_auth.api_key_config.api_key_secret_version,
        )
    elif _check_vertex_vector_search(gapic_vector_db):
        vector_config.vector_db = VertexVectorSearch(
            index_endpoint=gapic_vector_db.vertex_vector_search.index_endpoint,
            index=gapic_vector_db.vertex_vector_search.index,
        )
    elif _check_rag_managed_db(gapic_vector_db):
        vector_config.vector_db = RagManagedDb()
    if _check_rag_embedding_model_config(gapic_vector_db):
        vector_config.rag_embedding_model_config = (
            convert_gapic_to_rag_embedding_model_config(
                gapic_vector_db.rag_embedding_model_config
            )
        )
    return vector_config


def convert_gapic_to_rag_corpus(gapic_rag_corpus: GapicRagCorpus) -> RagCorpus:
    """Convert GapicRagCorpus to RagCorpus."""
    rag_corpus = RagCorpus(
        name=gapic_rag_corpus.name,
        display_name=gapic_rag_corpus.display_name,
        description=gapic_rag_corpus.description,
        embedding_model_config=convert_gapic_to_embedding_model_config(
            gapic_rag_corpus.rag_embedding_model_config
        ),
        vector_db=convert_gapic_to_vector_db(gapic_rag_corpus.rag_vector_db_config),
        vertex_ai_search_config=convert_gapic_to_vertex_ai_search_config(
            gapic_rag_corpus.vertex_ai_search_config
        ),
        backend_config=convert_gapic_to_backend_config(
            gapic_rag_corpus.rag_vector_db_config
        ),
    )
    return rag_corpus


def convert_gapic_to_rag_corpus_no_embedding_model_config(
    gapic_rag_corpus: GapicRagCorpus,
) -> RagCorpus:
    """Convert GapicRagCorpus without embedding model config (for UpdateRagCorpus) to RagCorpus."""
    rag_vector_db_config_no_embedding_model_config = gapic_rag_corpus.vector_db_config
    rag_vector_db_config_no_embedding_model_config.rag_embedding_model_config = None
    rag_corpus = RagCorpus(
        name=gapic_rag_corpus.name,
        display_name=gapic_rag_corpus.display_name,
        description=gapic_rag_corpus.description,
        vector_db=convert_gapic_to_vector_db(gapic_rag_corpus.rag_vector_db_config),
        vertex_ai_search_config=convert_gapic_to_vertex_ai_search_config(
            gapic_rag_corpus.vertex_ai_search_config
        ),
        backend_config=convert_gapic_to_backend_config(
            rag_vector_db_config_no_embedding_model_config
        ),
    )
    return rag_corpus


def convert_gapic_to_rag_file(gapic_rag_file: GapicRagFile) -> RagFile:
    """Convert GapicRagFile to RagFile."""
    rag_file = RagFile(
        name=gapic_rag_file.name,
        display_name=gapic_rag_file.display_name,
        description=gapic_rag_file.description,
    )
    return rag_file


def convert_json_to_rag_file(upload_rag_file_response: Dict[str, Any]) -> RagFile:
    """Converts a JSON response to a RagFile."""
    rag_file = RagFile(
        name=upload_rag_file_response.get("ragFile").get("name"),
        display_name=upload_rag_file_response.get("ragFile").get("displayName"),
        description=upload_rag_file_response.get("ragFile").get("description"),
    )
    return rag_file


def convert_path_to_resource_id(
    path: str,
) -> Union[str, GoogleDriveSource.ResourceId]:
    """Converts a path to a Google Cloud storage uri or GoogleDriveSource.ResourceId."""
    if path.startswith("gs://"):
        # Google Cloud Storage source
        return path
    elif path.startswith("https://drive.google.com/"):
        # Google Drive source
        path_list = path.split("/")
        if "file" in path_list:
            index = path_list.index("file") + 2
            resource_id = path_list[index].split("?")[0]
            resource_type = GoogleDriveSource.ResourceId.ResourceType.RESOURCE_TYPE_FILE
        elif "folders" in path_list:
            index = path_list.index("folders") + 1
            resource_id = path_list[index].split("?")[0]
            resource_type = (
                GoogleDriveSource.ResourceId.ResourceType.RESOURCE_TYPE_FOLDER
            )
        else:
            raise ValueError("path %s is not a valid Google Drive url.", path)

        return GoogleDriveSource.ResourceId(
            resource_id=resource_id,
            resource_type=resource_type,
        )
    else:
        raise ValueError(
            "path must be a Google Cloud Storage uri or a Google Drive url."
        )


def convert_source_for_rag_import(
    source: Union[SlackChannelsSource, JiraSource, SharePointSources]
) -> Union[GapicSlackSource, GapicJiraSource]:
    """Converts a SlackChannelsSource or JiraSource to a GapicSlackSource or GapicJiraSource."""
    if isinstance(source, SlackChannelsSource):
        result_source_channels = []
        for channel in source.channels:
            api_key = channel.api_key
            cid = channel.channel_id
            start_time = channel.start_time
            end_time = channel.end_time
            result_channels = GapicSlackSource.SlackChannels(
                channels=[
                    GapicSlackSource.SlackChannels.SlackChannel(
                        channel_id=cid,
                        start_time=start_time,
                        end_time=end_time,
                    )
                ],
                api_key_config=api_auth.ApiAuth.ApiKeyConfig(
                    api_key_secret_version=api_key
                ),
            )
            result_source_channels.append(result_channels)
        return GapicSlackSource(
            channels=result_source_channels,
        )
    elif isinstance(source, JiraSource):
        result_source_queries = []
        for query in source.queries:
            api_key = query.api_key
            custom_queries = query.custom_queries
            projects = query.jira_projects
            email = query.email
            server_uri = query.server_uri
            result_query = GapicJiraSource.JiraQueries(
                custom_queries=custom_queries,
                projects=projects,
                email=email,
                server_uri=server_uri,
                api_key_config=api_auth.ApiAuth.ApiKeyConfig(
                    api_key_secret_version=api_key
                ),
            )
            result_source_queries.append(result_query)
        return GapicJiraSource(
            jira_queries=result_source_queries,
        )
    elif isinstance(source, SharePointSources):
        result_source_share_point_sources = []
        for share_point_source in source.share_point_sources:
            sharepoint_folder_path = share_point_source.sharepoint_folder_path
            sharepoint_folder_id = share_point_source.sharepoint_folder_id
            drive_name = share_point_source.drive_name
            drive_id = share_point_source.drive_id
            client_id = share_point_source.client_id
            client_secret = share_point_source.client_secret
            tenant_id = share_point_source.tenant_id
            sharepoint_site_name = share_point_source.sharepoint_site_name
            result_share_point_source = GapicSharePointSources.SharePointSource(
                client_id=client_id,
                client_secret=api_auth.ApiAuth.ApiKeyConfig(
                    api_key_secret_version=client_secret
                ),
                tenant_id=tenant_id,
                sharepoint_site_name=sharepoint_site_name,
            )
            if sharepoint_folder_path is not None and sharepoint_folder_id is not None:
                raise ValueError(
                    "sharepoint_folder_path and sharepoint_folder_id cannot both be set."
                )
            elif sharepoint_folder_path is not None:
                result_share_point_source.sharepoint_folder_path = (
                    sharepoint_folder_path
                )
            elif sharepoint_folder_id is not None:
                result_share_point_source.sharepoint_folder_id = sharepoint_folder_id
            if drive_name is not None and drive_id is not None:
                raise ValueError("drive_name and drive_id cannot both be set.")
            elif drive_name is not None:
                result_share_point_source.drive_name = drive_name
            elif drive_id is not None:
                result_share_point_source.drive_id = drive_id
            else:
                raise ValueError("Either drive_name and drive_id must be set.")
            result_source_share_point_sources.append(result_share_point_source)
        return GapicSharePointSources(
            share_point_sources=result_source_share_point_sources,
        )
    else:
        raise TypeError(
            "source must be a SlackChannelsSource or JiraSource or SharePointSources."
        )


def prepare_import_files_request(
    corpus_name: str,
    paths: Optional[Sequence[str]] = None,
    source: Optional[Union[SlackChannelsSource, JiraSource, SharePointSources]] = None,
    chunk_size: int = 1024,
    chunk_overlap: int = 200,
    transformation_config: Optional[TransformationConfig] = None,
    max_embedding_requests_per_min: int = 1000,
    use_advanced_pdf_parsing: bool = False,
    partial_failures_sink: Optional[str] = None,
    layout_parser: Optional[LayoutParserConfig] = None,
    llm_parser: Optional[LlmParserConfig] = None,
) -> ImportRagFilesRequest:
    if len(corpus_name.split("/")) != 6:
        raise ValueError(
            "corpus_name must be of the format `projects/{project}/locations/{location}/ragCorpora/{rag_corpus}`"
        )

    rag_file_parsing_config = RagFileParsingConfig(
        advanced_parser=RagFileParsingConfig.AdvancedParser(
            use_advanced_pdf_parsing=use_advanced_pdf_parsing,
        ),
    )
    if layout_parser is not None:
        if (
            re.fullmatch(
                _VALID_DOCUMENT_AI_PROCESSOR_NAME_REGEX, layout_parser.processor_name
            )
            is None
        ):
            raise ValueError(
                "processor_name must be of the format "
                "`projects/{project_id}/locations/{location}/processors/{processor_id}`"
                "or "
                "`projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}`, "
                f"got {layout_parser.processor_name!r}"
            )
        rag_file_parsing_config.layout_parser = RagFileParsingConfig.LayoutParser(
            processor_name=layout_parser.processor_name,
            max_parsing_requests_per_min=layout_parser.max_parsing_requests_per_min,
        )
    if llm_parser is not None:
        rag_file_parsing_config.llm_parser = RagFileParsingConfig.LlmParser(
            model_name=llm_parser.model_name
        )
        if llm_parser.max_parsing_requests_per_min is not None:
            rag_file_parsing_config.llm_parser.max_parsing_requests_per_min = (
                llm_parser.max_parsing_requests_per_min
            )
        if llm_parser.custom_parsing_prompt is not None:
            rag_file_parsing_config.llm_parser.custom_parsing_prompt = (
                llm_parser.custom_parsing_prompt
            )

    local_chunk_size = chunk_size
    local_chunk_overlap = chunk_overlap
    if transformation_config and transformation_config.chunking_config:
        local_chunk_size = transformation_config.chunking_config.chunk_size
        local_chunk_overlap = transformation_config.chunking_config.chunk_overlap

    rag_file_transformation_config = RagFileTransformationConfig(
        rag_file_chunking_config=RagFileChunkingConfig(
            fixed_length_chunking=RagFileChunkingConfig.FixedLengthChunking(
                chunk_size=local_chunk_size,
                chunk_overlap=local_chunk_overlap,
            ),
        ),
    )
    import_rag_files_config = ImportRagFilesConfig(
        rag_file_transformation_config=rag_file_transformation_config,
        max_embedding_requests_per_min=max_embedding_requests_per_min,
        rag_file_parsing_config=rag_file_parsing_config,
    )

    if source is not None:
        gapic_source = convert_source_for_rag_import(source)
        if isinstance(gapic_source, GapicSlackSource):
            import_rag_files_config.slack_source = gapic_source
        if isinstance(gapic_source, GapicJiraSource):
            import_rag_files_config.jira_source = gapic_source
        if isinstance(gapic_source, GapicSharePointSources):
            import_rag_files_config.share_point_sources = gapic_source
    else:
        uris = []
        resource_ids = []
        for p in paths:
            output = convert_path_to_resource_id(p)
            if isinstance(output, str):
                uris.append(p)
            else:
                resource_ids.append(output)
        if uris:
            import_rag_files_config.gcs_source.uris = uris
        if resource_ids:
            google_drive_source = GoogleDriveSource(
                resource_ids=resource_ids,
            )
            import_rag_files_config.google_drive_source = google_drive_source

    if partial_failures_sink is not None:
        if partial_failures_sink.startswith("gs://"):
            import_rag_files_config.partial_failure_gcs_sink.output_uri_prefix = (
                partial_failures_sink
            )
        elif partial_failures_sink.startswith(
            "bq://"
        ) or partial_failures_sink.startswith("bigquery://"):
            import_rag_files_config.partial_failure_bigquery_sink.output_uri = (
                partial_failures_sink
            )
        else:
            raise ValueError(
                "if provided, partial_failures_sink must be a GCS path or a BigQuery table."
            )

    request = ImportRagFilesRequest(
        parent=corpus_name, import_rag_files_config=import_rag_files_config
    )
    return request


def get_corpus_name(
    name: str,
) -> str:
    if name:
        client = create_rag_data_service_client()
        if client.parse_rag_corpus_path(name):
            return name
        elif re.match("^{}$".format(_VALID_RESOURCE_NAME_REGEX), name):
            return client.rag_corpus_path(
                project=initializer.global_config.project,
                location=initializer.global_config.location,
                rag_corpus=name,
            )
        else:
            raise ValueError(
                "name must be of the format `projects/{project}/locations/{location}/ragCorpora/{rag_corpus}` or `{rag_corpus}`"
            )
    return name


def get_file_name(
    name: str,
    corpus_name: str,
) -> str:
    client = create_rag_data_service_client()
    if client.parse_rag_file_path(name):
        return name
    elif re.match("^{}$".format(_VALID_RESOURCE_NAME_REGEX), name):
        if not corpus_name:
            raise ValueError(
                "corpus_name must be provided if name is a `{rag_file}`, not a "
                "full resource name (`projects/{project}/locations/{location}/ragCorpora/{rag_corpus}/ragFiles/{rag_file}`). "
            )
        return client.rag_file_path(
            project=initializer.global_config.project,
            location=initializer.global_config.location,
            rag_corpus=get_corpus_name(corpus_name),
            rag_file=name,
        )
    else:
        raise ValueError(
            "name must be of the format `projects/{project}/locations/{location}/ragCorpora/{rag_corpus}/ragFiles/{rag_file}` or `{rag_file}`"
        )


def set_embedding_model_config(
    embedding_model_config: EmbeddingModelConfig,
    rag_corpus: GapicRagCorpus,
) -> None:
    if embedding_model_config.publisher_model and embedding_model_config.endpoint:
        raise ValueError("publisher_model and endpoint cannot be set at the same time.")
    if (
        not embedding_model_config.publisher_model
        and not embedding_model_config.endpoint
    ):
        raise ValueError("At least one of publisher_model and endpoint must be set.")
    parent = initializer.global_config.common_location_path(project=None, location=None)

    if embedding_model_config.publisher_model:
        publisher_model = embedding_model_config.publisher_model
        full_resource_name = re.match(
            r"^projects/(?P<project>.+?)/locations/(?P<location>.+?)/publishers/google/models/(?P<model_id>.+?)$",
            publisher_model,
        )
        resource_name = re.match(
            r"^publishers/google/models/(?P<model_id>.+?)$",
            publisher_model,
        )
        if full_resource_name:
            rag_corpus.rag_embedding_model_config.vertex_prediction_endpoint.endpoint = (
                publisher_model
            )
        elif resource_name:
            rag_corpus.rag_embedding_model_config.vertex_prediction_endpoint.endpoint = (
                parent + "/" + publisher_model
            )
        else:
            raise ValueError(
                "publisher_model must be of the format `projects/{project}/locations/{location}/publishers/google/models/{model_id}` or `publishers/google/models/{model_id}`"
            )

    if embedding_model_config.endpoint:
        endpoint = embedding_model_config.endpoint
        full_resource_name = re.match(
            r"^projects/(?P<project>.+?)/locations/(?P<location>.+?)/endpoints/(?P<endpoint>.+?)$",
            endpoint,
        )
        resource_name = re.match(
            r"^endpoints/(?P<endpoint>.+?)$",
            endpoint,
        )
        if full_resource_name:
            rag_corpus.rag_embedding_model_config.vertex_prediction_endpoint.endpoint = (
                endpoint
            )
        elif resource_name:
            rag_corpus.rag_embedding_model_config.vertex_prediction_endpoint.endpoint = (
                parent + "/" + endpoint
            )
        else:
            raise ValueError(
                "endpoint must be of the format `projects/{project}/locations/{location}/endpoints/{endpoint}` or `endpoints/{endpoint}`"
            )


def set_vector_db(
    vector_db: Union[
        Weaviate, VertexFeatureStore, VertexVectorSearch, Pinecone, RagManagedDb, None
    ],
    rag_corpus: GapicRagCorpus,
) -> None:
    """Sets the vector db configuration for the rag corpus."""
    if vector_db is None or isinstance(vector_db, RagManagedDb):
        rag_corpus.rag_vector_db_config = GapicRagVectorDbConfig(
            rag_managed_db=GapicRagVectorDbConfig.RagManagedDb(),
        )
    elif isinstance(vector_db, Weaviate):
        http_endpoint = vector_db.weaviate_http_endpoint
        collection_name = vector_db.collection_name
        api_key = vector_db.api_key

        rag_corpus.rag_vector_db_config = GapicRagVectorDbConfig(
            weaviate=GapicRagVectorDbConfig.Weaviate(
                http_endpoint=http_endpoint,
                collection_name=collection_name,
            ),
            api_auth=api_auth.ApiAuth(
                api_key_config=api_auth.ApiAuth.ApiKeyConfig(
                    api_key_secret_version=api_key
                ),
            ),
        )
    elif isinstance(vector_db, VertexFeatureStore):
        resource_name = vector_db.resource_name

        rag_corpus.rag_vector_db_config = GapicRagVectorDbConfig(
            vertex_feature_store=GapicRagVectorDbConfig.VertexFeatureStore(
                feature_view_resource_name=resource_name,
            ),
        )
    elif isinstance(vector_db, VertexVectorSearch):
        index_endpoint = vector_db.index_endpoint
        index = vector_db.index

        rag_corpus.rag_vector_db_config = GapicRagVectorDbConfig(
            vertex_vector_search=GapicRagVectorDbConfig.VertexVectorSearch(
                index_endpoint=index_endpoint,
                index=index,
            ),
        )
    elif isinstance(vector_db, Pinecone):
        index_name = vector_db.index_name
        api_key = vector_db.api_key

        rag_corpus.rag_vector_db_config = GapicRagVectorDbConfig(
            pinecone=GapicRagVectorDbConfig.Pinecone(
                index_name=index_name,
            ),
            api_auth=api_auth.ApiAuth(
                api_key_config=api_auth.ApiAuth.ApiKeyConfig(
                    api_key_secret_version=api_key
                ),
            ),
        )
    else:
        raise TypeError(
            "vector_db must be a Weaviate, VertexFeatureStore, VertexVectorSearch, RagManagedDb, or Pinecone."
        )


def set_vertex_ai_search_config(
    vertex_ai_search_config: VertexAiSearchConfig,
    rag_corpus: GapicRagCorpus,
) -> None:
    if not vertex_ai_search_config.serving_config:
        raise ValueError("serving_config must be set.")
    engine_resource_name = re.match(
        r"^projects/(?P<project>.+?)/locations/(?P<location>.+?)/collections/(?P<collection>.+?)/engines/(?P<engine>.+?)/servingConfigs/(?P<serving_config>.+?)$",
        vertex_ai_search_config.serving_config,
    )
    data_store_resource_name = re.match(
        r"^projects/(?P<project>.+?)/locations/(?P<location>.+?)/collections/(?P<collection>.+?)/dataStores/(?P<data_store>.+?)/servingConfigs/(?P<serving_config>.+?)$",
        vertex_ai_search_config.serving_config,
    )
    if engine_resource_name or data_store_resource_name:
        rag_corpus.vertex_ai_search_config = GapicVertexAiSearchConfig(
            serving_config=vertex_ai_search_config.serving_config,
        )
    else:
        raise ValueError(
            "serving_config must be of the format `projects/{project}/locations/{location}/collections/{collection}/engines/{engine}/servingConfigs/{serving_config}` or `projects/{project}/locations/{location}/collections/{collection}/dataStores/{data_store}/servingConfigs/{serving_config}`"
        )


def set_backend_config(
    backend_config: Optional[
        Union[
            RagVectorDbConfig,
            None,
        ]
    ],
    rag_corpus: GapicRagCorpus,
) -> None:
    """Sets the vector db configuration for the rag corpus."""
    if backend_config is None:
        return

    if backend_config.vector_db is not None:
        vector_config = backend_config.vector_db
        if vector_config is None or isinstance(vector_config, RagManagedDb):
            rag_corpus.vector_db_config.rag_managed_db.CopyFrom(
                GapicRagVectorDbConfig.RagManagedDb()
            )
        elif isinstance(vector_config, VertexVectorSearch):
            index_endpoint = vector_config.index_endpoint
            index = vector_config.index

            rag_corpus.vector_db_config.vertex_vector_search.index_endpoint = (
                index_endpoint
            )
            rag_corpus.vector_db_config.vertex_vector_search.index = index
        elif isinstance(vector_config, Pinecone):
            index_name = vector_config.index_name
            api_key = vector_config.api_key

            rag_corpus.vector_db_config.pinecone.index_name = index_name
            rag_corpus.vector_db_config.api_auth.api_key_config.api_key_secret_version = (
                api_key
            )
        else:
            raise TypeError(
                "backend_config must be a VertexFeatureStore,"
                "RagManagedDb, or Pinecone."
            )
        if backend_config.rag_embedding_model_config:
            set_embedding_model_config(
                backend_config.rag_embedding_model_config, rag_corpus
            )
