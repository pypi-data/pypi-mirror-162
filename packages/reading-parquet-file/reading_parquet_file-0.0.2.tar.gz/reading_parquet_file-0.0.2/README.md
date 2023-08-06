READ PARQUET FILES FROM AZURE BLOB STORAGE/ AZURE DATALAKE GEN 2

PARAMETERS

account_name: name of the storage account
container: storage blob container name
fname: file name/ file path inside the container
credentials: Account key for the storage account. Can also use DefaultAzureCredential if identity is enabled

OUTPUT:

Returns a pandas dataframe with all the file contents