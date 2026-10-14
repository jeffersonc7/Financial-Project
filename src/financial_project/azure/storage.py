import os

from azure.storage.filedatalake import DataLakeServiceClient

from financial_project.azure.auth import get_credential


def get_service_client():
    """Create an authenticated ADLS Gen2 service client."""
    account_name = os.environ["AZURE_STORAGE_ACCOUNT"]
    account_url = f"https://{account_name}.dfs.core.windows.net"

    return DataLakeServiceClient(
        account_url=account_url,
        credential=get_credential(),
    )


def get_filesystem(filesystem_name):
    """Get a filesystem from the storage account."""
    service_client = get_service_client()

    return service_client.get_file_system_client(
        file_system=filesystem_name
    )