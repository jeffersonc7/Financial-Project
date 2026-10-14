from azure.identity import DefaultAzureCredential


def get_credential():
    """Create an Azure credential."""
    return DefaultAzureCredential()