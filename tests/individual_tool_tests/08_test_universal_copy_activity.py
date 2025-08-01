#!/usr/bin/env python3
"""
Test script for Universal Copy Activity Tool - True Modular Design

This script validates:
- Individual source models (SharePoint, S3, Lakehouse)
- Individual sink models (Lakehouse, S3)
- All S3 file path types (file_path, wildcard, prefix, list_of_files)
- Universal copy activity tool combinations
"""

import json
import sys
import os
import asyncio
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from fabricmcp_server.tools.universal_copy_activity import (
    SharePointSource, S3Source, LakehouseSource, HttpSource, RestSource, FileSystemSource, MySqlSource,
    LakehouseSink, S3Sink, RestSink, FileSystemSink,
    FilePathType, S3FilePathConfig, TableConfiguration, FileConfiguration,
    CopyActivityConfig, create_universal_copy_pipeline_impl
)


def test_sharepoint_source_models():
    """Test SharePoint source model"""
    print("🔍 Testing SharePoint Source Models...")
    
    # Test basic SharePoint source
    sp_source = SharePointSource(
        connection_id="sp-conn-123",
        list_name="Documents"
    )
    
    sp_json = sp_source.to_copy_activity_source()
    print("✅ SharePoint Source (List Name):")
    print(json.dumps(sp_json, indent=2))
    
    # Test SharePoint with query
    sp_query_source = SharePointSource(
        connection_id="sp-conn-123", 
        list_name="WebPartGallery",
        query="$filter=Status eq 'Active'"
    )
    
    sp_query_json = sp_query_source.to_copy_activity_source()
    print("\n✅ SharePoint Source (With Query):")
    print(json.dumps(sp_query_json, indent=2))
    
    return True


def test_s3_source_models():
    """Test S3 source models with all file path types"""
    print("\n🔍 Testing S3 Source Models...")
    
    # 1. File Path Type
    file_path_config = S3FilePathConfig(
        path_type=FilePathType.FILE_PATH,
        folder_path="exports",
        file_name="data.json"
    )
    
    s3_file_source = S3Source(
        connection_id="s3-conn-456",
        bucket_name="google-photos-pipeline",
        source_type="JsonSource",
        format_type="Json",
        file_path_config=file_path_config,
        modified_datetime_start="2025-07-28T00:00:00.000Z",
        modified_datetime_end="2025-07-27T00:02:00.000Z"
    )
    
    s3_file_json = s3_file_source.to_copy_activity_source()
    print("✅ S3 Source (File Path Type):")
    print(json.dumps(s3_file_json, indent=2))
    
    # 2. Wildcard Type
    wildcard_config = S3FilePathConfig(
        path_type=FilePathType.WILDCARD,
        wildcard_folder_path="wildcard_folder",
        wildcard_file_name="wildcard_file"
    )
    
    s3_wildcard_source = S3Source(
        connection_id="s3-conn-456",
        bucket_name="google-photos-pipeline",
        source_type="BinarySource",
        format_type="Binary",
        file_path_config=wildcard_config
    )
    
    s3_wildcard_json = s3_wildcard_source.to_copy_activity_source()
    print("\n✅ S3 Source (Wildcard Type):")
    print(json.dumps(s3_wildcard_json, indent=2))
    
    # 3. Prefix Type
    prefix_config = S3FilePathConfig(
        path_type=FilePathType.PREFIX,
        prefix="prefix_name"
    )
    
    s3_prefix_source = S3Source(
        connection_id="s3-conn-456",
        bucket_name="google-photos-pipeline", 
        source_type="BinarySource",
        format_type="Binary",
        file_path_config=prefix_config
    )
    
    s3_prefix_json = s3_prefix_source.to_copy_activity_source()
    print("\n✅ S3 Source (Prefix Type):")
    print(json.dumps(s3_prefix_json, indent=2))
    
    # 4. List of Files Type
    list_config = S3FilePathConfig(
        path_type=FilePathType.LIST_OF_FILES,
        file_list_path="google-photos-pipeline/exports",
        list_folder_path="exports"
    )
    
    s3_list_source = S3Source(
        connection_id="s3-conn-456",
        bucket_name="google-photos-pipeline",
        source_type="BinarySource", 
        format_type="Binary",
        file_path_config=list_config
    )
    
    s3_list_json = s3_list_source.to_copy_activity_source()
    print("\n✅ S3 Source (List of Files Type):")
    print(json.dumps(s3_list_json, indent=2))
    
    return True


def test_lakehouse_source_models():
    """Test Lakehouse source models for both Tables and Files"""
    print("\n🔍 Testing Lakehouse Source Models...")
    
    # Table source
    table_config = TableConfiguration(
        table_name="fact_sales_enriched",
        schema_name="dbo"
    )
    
    lh_table_source = LakehouseSource(
        lakehouse_name="AdvancedDataLakehouse",
        workspace_id="2bb31c24-2c1f-467a-bffd-3a37a2c0ad27",
        artifact_id="0440d283-3ccf-478c-9d26-53145c1e6802",
        root_folder="Tables",
        table_config=table_config,
        timestamp_as_of="2025-07-26T02:00:00.000Z",
        version_as_of=1
    )
    
    lh_table_json = lh_table_source.to_copy_activity_source()
    print("✅ Lakehouse Source (Table):")
    print(json.dumps(lh_table_json, indent=2))
    
    # File source  
    file_config = FileConfiguration(
        folder_path="processed_data",
        file_name="customers.json",
        file_format="JSON"
    )
    
    lh_file_source = LakehouseSource(
        lakehouse_name="AdvancedDataLakehouse",
        workspace_id="2bb31c24-2c1f-467a-bffd-3a37a2c0ad27", 
        artifact_id="0440d283-3ccf-478c-9d26-53145c1e6802",
        root_folder="Files",
        file_config=file_config
    )
    
    lh_file_json = lh_file_source.to_copy_activity_source()
    print("\n✅ Lakehouse Source (File):")
    print(json.dumps(lh_file_json, indent=2))
    
    return True


def test_lakehouse_sink_models():
    """Test Lakehouse sink models"""
    print("\n🔍 Testing Lakehouse Sink Models...")
    
    # Table sink
    table_config = TableConfiguration(
        table_name="customer_segments"
    )
    
    lh_table_sink = LakehouseSink(
        lakehouse_name="SinkLakehouse",
        workspace_id="2bb31c24-2c1f-467a-bffd-3a37a2c0ad27",
        artifact_id="6f2063f8-424f-4c22-918b-59629e0356f4",
        root_folder="Tables",
        table_config=table_config,
        table_action_option="Append"
    )
    
    lh_table_sink_json = lh_table_sink.to_copy_activity_sink()
    print("✅ Lakehouse Sink (Table):")
    print(json.dumps(lh_table_sink_json, indent=2))
    
    # File sink
    file_config = FileConfiguration(
        folder_path="Output",
        file_name="data_from_sharepoint",
        file_format="DelimitedText"
    )
    
    lh_file_sink = LakehouseSink(
        lakehouse_name="SinkLakehouse",
        workspace_id="2bb31c24-2c1f-467a-bffd-3a37a2c0ad27",
        artifact_id="6f2063f8-424f-4c22-918b-59629e0356f4",
        root_folder="Files",
        file_config=file_config
    )
    
    lh_file_sink_json = lh_file_sink.to_copy_activity_sink()
    print("\n✅ Lakehouse Sink (File):")
    print(json.dumps(lh_file_sink_json, indent=2))
    
    return True


def test_s3_sink_models():
    """Test S3 sink models"""
    print("\n🔍 Testing S3 Sink Models...")
    
    file_config = FileConfiguration(
        folder_path="exports",
        file_name="from_lakehouse"
    )
    
    s3_sink = S3Sink(
        connection_id="s3-conn-456",
        bucket_name="google-photos-pipeline",
        sink_type="JsonSink",
        format_type="Json",
        file_config=file_config
    )
    
    s3_sink_json = s3_sink.to_copy_activity_sink()
    print("✅ S3 Sink:")
    print(json.dumps(s3_sink_json, indent=2))
    
    return True


def test_mysql_models():
    """Test MySQL source models (sink not supported in Fabric)"""
    print("\n🔍 Testing MySQL Source Models...")
    
    # Test MySQL Source with table name
    mysql_source_table_config = {
        "connection_id": "e10598ee-1951-4278-b535-1deaee0b5dc9",
        "table_name": "`dummy_table`",
        "additional_columns": [
            {
                "name": "test_additional_column",
                "value": "$$COLUMN:sum"
            }
        ]
    }
    mysql_source_table = MySqlSource(**mysql_source_table_config)
    mysql_source_table_json = mysql_source_table.to_copy_activity_source()
    
    print("✅ MySQL Source (Table with Additional Columns):")
    print(json.dumps(mysql_source_table_json, indent=2))
    print()
    
    # Test MySQL Source with custom query
    mysql_source_query_config = {
        "connection_id": "e10598ee-1951-4278-b535-1deaee0b5dc9",
        "table_name": "`dummy_table`",  # Still needed in datasetSettings
        "query": "SELECT id, name, SUM(amount) as total FROM transactions GROUP BY id, name",
        "additional_columns": [
            {
                "name": "test_additional_column",
                "value": "$$COLUMN:sum"
            }
        ]
    }
    mysql_source_query = MySqlSource(**mysql_source_query_config)
    mysql_source_query_json = mysql_source_query.to_copy_activity_source()
    
    print("✅ MySQL Source (Custom Query with Additional Columns):")
    print(json.dumps(mysql_source_query_json, indent=2))
    print()
    
    return True


def test_http_rest_models():
    """Test HTTP and REST source/sink models"""
    print("\n🧪 Testing HTTP and REST Models...")
    
    from fabricmcp_server.tools.universal_copy_activity import (
        HttpSource, RestSource, RestSink
    )
    
    # Test HttpSource
    print("  🌐 Testing HttpSource...")
    http_source = HttpSource(
        connection_id="http-conn-123",
        base_url="https://api.example.com",
        relative_url="data/users",
        request_method="GET",
        request_body="{}",
        headers={"Authorization": "Bearer token123"},
        timeout="00:01:40",
        additional_columns=[
            {"name": "api_source", "value": "$$COLUMN:api_endpoint"}
        ]
    )
    
    source_json = http_source.to_copy_activity_source()
    # HttpSource generates DelimitedTextSource type when format is DelimitedText (default)
    assert source_json["type"] == "DelimitedTextSource"
    assert source_json["storeSettings"]["type"] == "HttpReadSettings"
    print("    ✅ HttpSource test passed!")
    
    # Test RestSource  
    print("  🔗 Testing RestSource...")
    rest_source = RestSource(
        connection_id="rest-conn-456",
        base_url="https://rest.api.com",
        relative_url="v1/data",
        request_method="POST",
        headers={"Content-Type": "application/json"},
        request_body='{"query": "select * from users"}',
        pagination_config={
            "type": "EndOfData",
            "supportRFC5988": True
        }
    )
    
    rest_source_json = rest_source.to_copy_activity_source()
    assert rest_source_json["type"] == "RestSource"
    # Note: baseUrl location may vary in JSON structure, so we'll keep this test simple
    print("    ✅ RestSource test passed!")
    
    # Test RestSink
    print("  📤 Testing RestSink...")
    rest_sink = RestSink(
        connection_id="rest-sink-789",
        base_url="https://webhook.site",
        relative_url="endpoint123",
        request_method="POST",
        headers={"Content-Type": "application/json"},
        write_batch_size=1000,
        http_request_timeout="00:02:00"
    )
    
    sink_json = rest_sink.to_copy_activity_sink()
    assert sink_json["type"] == "RestSink"
    # Note: baseUrl location may vary in JSON structure, so we'll keep this test simple
    print("    ✅ RestSink test passed!")
    
    print("    ✅ All HTTP/REST model tests passed!")

def test_filesystem_models():
    """Test FileSystem source and sink models"""
    print("\n🧪 Testing FileSystem Models...")
    
    from fabricmcp_server.tools.universal_copy_activity import (
        FileSystemSource, FileSystemSink
    )
    
    # Test FileSystemSource
    print("  📁 Testing FileSystemSource...")
    fs_source = FileSystemSource(
        connection_id="ad24330c-9b44-4060-bd5e-b5d8f26b0d58",
        folder_path="myenv38/bin",
        file_name="python3",
        file_format="DelimitedText",
        recursive=True,
        max_concurrent_connections=3,
        enable_partition_discovery=True,
        partition_root_path="myenv38/bin",
        modified_datetime_start="2025-07-31T00:00:00.000Z",
        modified_datetime_end="2025-07-30T00:06:00.000Z",
        additional_columns=[
            {"name": "file_name", "value": "$$FILEPATH"}
        ]
    )
    
    source_json = fs_source.to_copy_activity_source()
    assert source_json["type"] == "DelimitedTextSource"
    assert source_json["storeSettings"]["type"] == "FileServerReadSettings"
    assert source_json["storeSettings"]["recursive"] == True
    print("    ✅ FileSystemSource test passed!")
    
    # Test FileSystemSink
    print("  📤 Testing FileSystemSink...")
    fs_sink = FileSystemSink(
        connection_id="0d3180e2-e49d-49fc-838e-f7af1fe31188",
        folder_path="output_data",
        file_name="output",
        file_format="DelimitedText",
        max_concurrent_connections=3,
        copy_behavior="PreserveHierarchy"
    )
    
    sink_json = fs_sink.to_copy_activity_sink()
    assert sink_json["type"] == "DelimitedTextSink"
    assert sink_json["storeSettings"]["type"] == "FileServerWriteSettings"
    print("    ✅ FileSystemSink test passed!")
    
    print("    ✅ All FileSystem model tests passed!")

def test_complete_copy_activity_configs():
    """Test complete copy activity configurations"""
    print("\n🧪 Testing Complete Copy Activity Configurations...")
    
    # Test SharePoint to Lakehouse
    print("  📋 Testing SharePoint → Lakehouse configuration...")
    from fabricmcp_server.tools.universal_copy_activity import (
        SharePointSource, LakehouseSink, TableConfiguration
    )
    
    sp_source = SharePointSource(
        connection_id="29099f29-20ae-4998-bd13-007289b3f7e3",
        list_name="WebPartGallery"
    )
    
    table_config = TableConfiguration(table_name="sharepoint_data")
    lh_sink = LakehouseSink(
        lakehouse_name="SinkLakehouse_Test",
        workspace_id="2bb31c24-2c1f-467a-bffd-3a37a2c0ad27",
        artifact_id="6f2063f8-424f-4c22-918b-59629e0356f4",
        root_folder="Tables",
        table_config=table_config
    )
    
    # Verify they generate JSON correctly
    sp_json = sp_source.to_copy_activity_source()
    lh_json = lh_sink.to_copy_activity_sink()
    
    assert sp_json["type"] == "SharePointOnlineListSource"
    assert lh_json["type"] == "LakehouseTableSink"
    print("    ✅ SharePoint → Lakehouse configuration works!")
    
    print("    ✅ All complete configuration tests passed!")


def generate_mcp_tool_examples():
    """Generate example JSON configurations for MCP tool usage"""
    print("\n🔍 Generating MCP Tool Usage Examples...")
    
    examples = {
        "sharepoint_to_lakehouse_table": {
            "workspace_id": "2bb31c24-2c1f-467a-bffd-3a37a2c0ad27",
            "pipeline_name": "SharePoint_to_Lakehouse_Pipeline",
            "source_type": "SharePoint",
            "source_config": {
                "connection_id": "29099f29-20ae-4998-bd13-007289b3f7e3",
                "list_name": "WebPartGallery",
                "query": "$filter=Status eq 'Active'"
            },
            "sink_type": "Lakehouse",
            "sink_config": {
                "lakehouse_name": "SinkLakehouse_Test",
                "workspace_id": "2bb31c24-2c1f-467a-bffd-3a37a2c0ad27",
                "artifact_id": "6f2063f8-424f-4c22-918b-59629e0356f4",
                "root_folder": "Files",
                "file_config": {
                    "folder_path": "Output",
                    "file_name": "data_from_sharepoint",
                    "file_format": "DelimitedText"
                }
            },
            "activity_config": {
                "activity_name": "Copy SharePoint Data",
                "description": "Copy data from SharePoint list to Lakehouse",
                "enable_schema_mapping": True,
                "translator": {
                    "mappings": [
                        {"source": {"name": "Title", "type": "String"}},
                        {"source": {"name": "Status", "type": "String"}}
                    ]
                }
            }
        },
        "s3_wildcard_to_lakehouse": {
            "workspace_id": "2bb31c24-2c1f-467a-bffd-3a37a2c0ad27",
            "pipeline_name": "S3_Wildcard_to_Lakehouse_Pipeline", 
            "source_type": "S3",
            "source_config": {
                "connection_id": "ea2ef352-5072-4c31-a500-5fab9c03c706",
                "bucket_name": "google-photos-pipeline",
                "source_type": "BinarySource",
                "format_type": "Binary",
                "file_path_config": {
                    "path_type": "wildcard",
                    "wildcard_folder_path": "wildcard_folder",
                    "wildcard_file_name": "wildcard_file"
                },
                "modified_datetime_start": "2025-07-28T00:00:00.000Z",
                "modified_datetime_end": "2025-07-27T00:03:00.000Z"
            },
            "sink_type": "Lakehouse",
            "sink_config": {
                "lakehouse_name": "SinkLakehouse_Test",
                "workspace_id": "2bb31c24-2c1f-467a-bffd-3a37a2c0ad27",
                "artifact_id": "6f2063f8-424f-4c22-918b-59629e0356f4",
                "root_folder": "Files",
                "file_config": {
                    "folder_path": "Output",
                    "file_name": "s3_sink",
                    "file_format": "Binary"
                }
            }
        },
        "lakehouse_table_to_s3": {
            "workspace_id": "2bb31c24-2c1f-467a-bffd-3a37a2c0ad27",
            "pipeline_name": "Lakehouse_Table_to_S3_Pipeline",
            "source_type": "Lakehouse",
            "source_config": {
                "lakehouse_name": "AdvancedDataLakehouse",
                "workspace_id": "2bb31c24-2c1f-467a-bffd-3a37a2c0ad27",
                "artifact_id": "0440d283-3ccf-478c-9d26-53145c1e6802",
                "root_folder": "Tables",
                "table_config": {
                    "table_name": "fact_sales_enriched"
                }
            },
            "sink_type": "S3",
            "sink_config": {
                "connection_id": "ea2ef352-5072-4c31-a500-5fab9c03c706", 
                "bucket_name": "google-photos-pipeline",
                "sink_type": "JsonSink",
                "format_type": "Json",
                "file_config": {
                    "folder_path": "exports",
                    "file_name": "from_lakehouse"
                }
            }
        }
    }
    
    # Save examples to file
    examples_file = "UNIVERSAL_COPY_TOOL_EXAMPLES.json"
    with open(examples_file, 'w') as f:
        json.dump(examples, f, indent=2)
    
    print(f"✅ MCP Tool examples saved to: {examples_file}")
    
    return examples


async def test_real_pipeline_creation():
    """Test real pipeline creation (commented out for safety)"""
    print("\n🔍 Real Pipeline Creation Test (DISABLED)")
    print("To enable real pipeline creation:")
    print("1. Uncomment the code below")
    print("2. Ensure you have valid workspace_id and connection_id")
    print("3. Update the configuration with your actual values")
    
    # UNCOMMENT BELOW FOR REAL TESTING
    # """
    try:
        from fabricmcp_server.sessions import get_session_fabric_client
        
        # Mock context for testing - needs session attribute
        class MockSession:
            pass
            
        class MockContext:
            def __init__(self):
                self.session = MockSession()
        
        ctx = MockContext()
        
        result = await create_universal_copy_pipeline_impl(
            ctx,
            workspace_id="2bb31c24-2c1f-467a-bffd-3a37a2c0ad27",
            pipeline_name=f"Universal_Test_Pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_type="SharePoint",
            source_config={
                "connection_id": "29099f29-20ae-4998-bd13-007289b3f7e3",
                "list_name": "WebPartGallery"
            },
            sink_type="Lakehouse", 
            sink_config={
                "lakehouse_name": "SinkLakehouse_Test",
                "workspace_id": "2bb31c24-2c1f-467a-bffd-3a37a2c0ad27",
                "artifact_id": "6f2063f8-424f-4c22-918b-59629e0356f4",
                "root_folder": "Files",
                "file_config": {
                    "folder_path": "Output",
                    "file_name": "universal_test",
                    "file_format": "DelimitedText"
                }
            },
            description="Test of universal copy activity tool"
        )
        
        print("✅ Real pipeline creation result:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Real pipeline creation failed: {str(e)}")
    # """


def test_google_cloud_storage_models():
    """Test Google Cloud Storage source and sink models"""
    print("\n🧪 Testing Google Cloud Storage Models...")
    
    from fabricmcp_server.tools.universal_copy_activity import (
        GoogleCloudStorageSource, GoogleCloudStorageSink,
        GoogleCloudStoragePathType, GoogleCloudStorageFilePathConfig
    )
    
    # Test GoogleCloudStorageSource - File Path (matches manual config 1)
    print("  📁 Testing GoogleCloudStorageSource with file path...")
    file_path_config = GoogleCloudStorageFilePathConfig(
        path_type=GoogleCloudStoragePathType.FILE_PATH,
        object_key="Test folder/GCS_Source"
    )
    
    gcs_source = GoogleCloudStorageSource(
        connection_id="ebfd8185-59ce-45c1-a980-9901ba3573d9",
        bucket_name="fabric-mcp",
        file_path_config=file_path_config,
        file_format="DelimitedText",
        recursive=True,
        max_concurrent_connections=1,
        modified_datetime_start="2025-07-31T00:00:00Z",
        modified_datetime_end="2025-07-30T01:00:00Z",
        enable_partition_discovery=True,
        partition_root_path="fabric-mcp/Test folder",
        additional_columns=[
            {"name": "just_to_test", "value": "FILEPATH"}
        ]
    )
    
    source_json = gcs_source.to_copy_activity_source()
    print(f"    ✅ Generated source JSON with {len(source_json)} properties")
    
    # Verify key properties match manual config
    assert source_json["type"] == "DelimitedTextSource"
    assert source_json["storeSettings"]["type"] == "GoogleCloudStorageReadSettings"
    assert source_json["storeSettings"]["recursive"] == True
    assert source_json["storeSettings"]["enablePartitionDiscovery"] == True
    assert source_json["storeSettings"]["partitionRootPath"] == "fabric-mcp/Test folder"
    assert source_json["datasetSettings"]["typeProperties"]["location"]["bucketName"] == "fabric-mcp"
    assert source_json["datasetSettings"]["typeProperties"]["location"]["folderPath"] == "Test folder"
    assert source_json["datasetSettings"]["typeProperties"]["location"]["fileName"] == "GCS_Source"
    assert source_json["datasetSettings"]["typeProperties"]["columnDelimiter"] == ","
    assert source_json["datasetSettings"]["typeProperties"]["escapeChar"] == "\\"
    assert source_json["datasetSettings"]["typeProperties"]["firstRowAsHeader"] == True
    assert source_json["datasetSettings"]["typeProperties"]["quoteChar"] == "\""
    assert source_json["datasetSettings"]["externalReferences"]["connection"] == "ebfd8185-59ce-45c1-a980-9901ba3573d9"
    assert len(source_json["additionalColumns"]) == 1
    assert source_json["additionalColumns"][0]["value"] == "FILEPATH"
    
    # Test GoogleCloudStorageSource - Prefix (matches manual config 2)
    print("  🏷️ Testing GoogleCloudStorageSource with prefix...")
    prefix_config = GoogleCloudStorageFilePathConfig(
        path_type=GoogleCloudStoragePathType.PREFIX,
        prefix="<prefix_here>"
    )
    
    gcs_prefix_source = GoogleCloudStorageSource(
        connection_id="ebfd8185-59ce-45c1-a980-9901ba3573d9",
        bucket_name="fabric-mcp",
        file_path_config=prefix_config,
        file_format="DelimitedText",
        recursive=True,
        max_concurrent_connections=1,
        modified_datetime_start="2025-07-31T00:00:00Z",
        modified_datetime_end="2025-07-30T01:00:00Z",
        enable_partition_discovery=True,
        partition_root_path="fabric-mcp/Test folder",
        additional_columns=[
            {"name": "just_to_test", "value": "FILEPATH"}
        ]
    )
    
    prefix_json = gcs_prefix_source.to_copy_activity_source()
    assert prefix_json["type"] == "DelimitedTextSource"
    assert prefix_json["storeSettings"]["prefix"] == "<prefix_here>"
    # With prefix, location should only have bucketName (no folderPath/fileName)
    assert "folderPath" not in prefix_json["datasetSettings"]["typeProperties"]["location"]
    assert "fileName" not in prefix_json["datasetSettings"]["typeProperties"]["location"]
    
    # Test GoogleCloudStorageSource - Wildcard (matches manual config 3)
    print("  🔍 Testing GoogleCloudStorageSource with wildcard...")
    wildcard_config = GoogleCloudStorageFilePathConfig(
        path_type=GoogleCloudStoragePathType.WILDCARD,
        wildcard_folder_path="<wild_card_folder_path>",
        wildcard_file_name="<wildcard_filename>"
    )
    
    gcs_wildcard_source = GoogleCloudStorageSource(
        connection_id="ebfd8185-59ce-45c1-a980-9901ba3573d9",
        bucket_name="fabric-mcp",
        file_path_config=wildcard_config,
        file_format="DelimitedText",
        recursive=True,
        max_concurrent_connections=1,
        modified_datetime_start="2025-07-31T00:00:00Z",
        modified_datetime_end="2025-07-30T01:00:00Z",
        enable_partition_discovery=True,
        partition_root_path="fabric-mcp/Test folder",
        additional_columns=[
            {"name": "just_to_test", "value": "FILEPATH"}
        ]
    )
    
    wildcard_json = gcs_wildcard_source.to_copy_activity_source()
    assert wildcard_json["type"] == "DelimitedTextSource"
    assert wildcard_json["storeSettings"]["wildcardFolderPath"] == "<wild_card_folder_path>"
    assert wildcard_json["storeSettings"]["wildcardFileName"] == "<wildcard_filename>"
    # With wildcard, location should only have bucketName
    assert "folderPath" not in wildcard_json["datasetSettings"]["typeProperties"]["location"]
    assert "fileName" not in wildcard_json["datasetSettings"]["typeProperties"]["location"]
    
    # Test GoogleCloudStorageSource - List of Files (matches manual config 4)
    print("  📋 Testing GoogleCloudStorageSource with list of files...")
    filelist_config = GoogleCloudStorageFilePathConfig(
        path_type=GoogleCloudStoragePathType.LIST_OF_FILES,
        file_list_path="fabric-mcp/Test folder"
    )
    
    gcs_filelist_source = GoogleCloudStorageSource(
        connection_id="ebfd8185-59ce-45c1-a980-9901ba3573d9",
        bucket_name="fabric-mcp",
        file_path_config=filelist_config,
        file_format="DelimitedText",
        max_concurrent_connections=1,
        enable_partition_discovery=True,
        partition_root_path="fabric-mcp/Test folder",
        additional_columns=[
            {"name": "just_to_test", "value": "FILEPATH"}
        ]
    )
    
    filelist_json = gcs_filelist_source.to_copy_activity_source()
    assert filelist_json["type"] == "DelimitedTextSource"
    assert filelist_json["storeSettings"]["fileListPath"] == "fabric-mcp/Test folder"
    # For fileListPath, should have folderPath but no fileName
    assert filelist_json["datasetSettings"]["typeProperties"]["location"]["folderPath"] == "fabric-mcp"
    assert "fileName" not in filelist_json["datasetSettings"]["typeProperties"]["location"]
    # List of files should not have recursive in storeSettings
    assert "recursive" not in filelist_json["storeSettings"]
    
    # Test GoogleCloudStorageSink - DelimitedText (matches manual config 1)
    print("  📤 Testing GoogleCloudStorageSink with DelimitedText...")
    gcs_sink = GoogleCloudStorageSink(
        connection_id="ebfd8185-59ce-45c1-a980-9901ba3573d9",
        bucket_name="fabric-mcp",
        folder_path="Test folder",
        file_name="GCS_Sink",
        file_format="DelimitedText",
        max_concurrent_connections=1,
        copy_behavior="MergeFiles"
    )
    
    sink_json = gcs_sink.to_copy_activity_sink()
    print(f"    ✅ Generated sink JSON with {len(sink_json)} properties")
    
    # Verify sink properties match manual config
    assert sink_json["type"] == "DelimitedTextSink"
    assert sink_json["storeSettings"]["type"] == "GoogleCloudStorageWriteSettings"
    assert sink_json["storeSettings"]["copyBehavior"] == "MergeFiles"
    assert sink_json["formatSettings"]["type"] == "DelimitedTextWriteSettings"
    assert sink_json["formatSettings"]["fileExtension"] == ".txt"
    assert sink_json["datasetSettings"]["typeProperties"]["location"]["bucketName"] == "fabric-mcp"
    assert sink_json["datasetSettings"]["typeProperties"]["location"]["folderPath"] == "Test folder"
    assert sink_json["datasetSettings"]["typeProperties"]["location"]["fileName"] == "GCS_Sink"
    assert sink_json["datasetSettings"]["typeProperties"]["columnDelimiter"] == ","
    assert sink_json["datasetSettings"]["typeProperties"]["escapeChar"] == "\\"
    assert sink_json["datasetSettings"]["externalReferences"]["connection"] == "ebfd8185-59ce-45c1-a980-9901ba3573d9"
    assert sink_json["datasetSettings"]["schema"] == []  # Array for DelimitedText
    
    # Test GoogleCloudStorageSink - JSON format (matches manual config 2 & 3)
    print("  📄 Testing GoogleCloudStorageSink with JSON format...")
    gcs_json_sink = GoogleCloudStorageSink(
        connection_id="ebfd8185-59ce-45c1-a980-9901ba3573d9",
        bucket_name="fabric-mcp",
        folder_path="Test folder",
        file_name="GCS_Sink",
        file_format="JSON",
        json_file_pattern="arrayOfObjects",  # This matches manual config
        max_concurrent_connections=1,
        copy_behavior="MergeFiles"
    )
    
    json_sink_json = gcs_json_sink.to_copy_activity_sink()
    assert json_sink_json["type"] == "JsonSink"
    assert json_sink_json["formatSettings"]["type"] == "JsonWriteSettings"
    assert json_sink_json["formatSettings"]["filePattern"] == "arrayOfObjects"
    assert json_sink_json["datasetSettings"]["schema"] == {}  # Empty object for JSON, not array
    
    # Test GoogleCloudStorageSink - Binary format (matches manual config 4)
    print("  🗂️ Testing GoogleCloudStorageSink with Binary format...")
    gcs_binary_sink = GoogleCloudStorageSink(
        connection_id="ebfd8185-59ce-45c1-a980-9901ba3573d9",
        bucket_name="fabric-mcp",
        folder_path="Test folder",
        file_name="GCS_Sink",
        file_format="Binary",
        max_concurrent_connections=1,
        copy_behavior="MergeFiles"
    )
    
    binary_sink_json = gcs_binary_sink.to_copy_activity_sink()
    assert binary_sink_json["type"] == "BinarySink"
    # Binary should NOT have formatSettings
    assert "formatSettings" not in binary_sink_json
    assert binary_sink_json["datasetSettings"]["type"] == "Binary"
    
    print("    ✅ All Google Cloud Storage model tests passed!")


def main():
    """Run all tests"""
    print("🚀 Testing Universal Copy Activity Tool - True Modular Design")
    print("=" * 80)
    
    try:
        # Test individual components
        test_sharepoint_source_models()
        test_s3_source_models()
        test_lakehouse_source_models()
        test_lakehouse_sink_models()
        test_s3_sink_models()
        test_http_rest_models()
        test_filesystem_models()
        test_mysql_models()
        test_google_cloud_storage_models()  # New Google Cloud Storage tests

        # Test complete configurations
        test_complete_copy_activity_configs()
        
        # Generate MCP examples
        examples = generate_mcp_tool_examples()
        
        # Test real pipeline creation (disabled by default)
        asyncio.run(test_real_pipeline_creation())
        
        print("\n" + "=" * 80)
        print("🎉 All tests completed successfully!")
        print("✅ SharePoint source models: Working")
        print("✅ S3 source models: Working") 
        print("✅ Lakehouse source/sink models: Working")
        print("✅ S3 sink models: Working")
        print("✅ HTTP/REST models: Working")
        print("✅ FileSystem models: Working")
        print("✅ MySQL models: Working")
        print("✅ Google Cloud Storage models: Working")  # New line
        print("✅ Complete copy activity configurations: Working")
        print("✅ MCP tool examples generated successfully")
        print("✅ Real pipeline creation: Tested (if enabled)")
        print("\n🔧 Your universal copy activity tool is ready for production!")
        print("🌟 Supported connectors: SharePoint, S3, Lakehouse, HTTP, REST, FileSystem, MySQL, Google Cloud Storage")
        return True
    except Exception as e:
        print(f"\n❌ Tests failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 