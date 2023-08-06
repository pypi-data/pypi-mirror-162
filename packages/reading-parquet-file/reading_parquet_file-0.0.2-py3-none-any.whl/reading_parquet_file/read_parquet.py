import pandas as pd
import pyarrow.fs
import pyarrowfs_adlgen2

def read_parquet(account_name, container, fname, credentials):
    handler = pyarrowfs_adlgen2.FilesystemHandler.from_account_name(
       account_name, container, credentials)
    fs = pyarrow.fs.PyFileSystem(handler)
    df = pd.read_parquet(fname,filesystem=fs)
    
    return df