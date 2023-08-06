import io
import time
import inspect
import requests
import pandas as pd
import dask.dataframe as dd

from .base import bucket_name, Base
from .dataset import DatasetManager
from .utils.requests import check_http_status_code

def append_slash(txt):
    if txt[-1] != '/':
        txt += '/'
    return txt

class DataNode(DatasetManager):
    def write(self, df=None, directory=None, name=None, description="", replace=None, profiling=False, **kwargs):
        if type(df) not in [pd.DataFrame, dd.DataFrame]:
            raise Exception(f"Invalid type expect ddf(dask dataframe) or df(pandas dataframe), Please input `df=`, but got {type(df)}")
        if name == None or type(name) != str:
            raise Exception(f"Please input data `name`=<str>, but got {type(name)}")
        if directory == None or type(directory) != int:
            raise Exception(f"Please input data `directory`=<int>, but got {type(directory)}")
        if description=="" or type(description)!=str:
            description = f"data {name}"
            
        name = f'{name}.parquet'
        replace = self._check_fileExists(directory, name)
        
        _res = requests.post(f'{self._discovery_api}/file/', headers=self._jwt_header,
                                json={
                                    "name": name,
                                    "description": description,
                                    "directory": directory,
                                    "is_use": False,
                                    "replace": replace
                                }
                            )
        if _res.status_code != 201:
            raise Exception(f"can not create directory in discovery {_res.json()}")
        meta = _res.json()
        df.to_parquet(f"s3://{bucket_name}/{meta['key']}",
            storage_options=self._storage_options,
            engine="pyarrow",
            **kwargs
        )
        
        # create profiling & data dict
        if profiling:
            for _ in range(5):
                _res = requests.get(f"{self._discovery_api}/file/{meta['id']}/", headers=self._jwt_header)
                if _res.status_code != 200:
                    time.sleep(2)
                else:
                    break
            requests.get(f"{self._discovery_api}/file/{meta['id']}/createDatadict/", headers=self._jwt_header)
            requests.get(f"{self._discovery_api}/file/{meta['id']}/createProfileling/", headers=self._jwt_header)
            
        return {
            'sucess': True,
            'file_id': meta['id'],
            'path': meta['path']
        }
    
    def get_file(self, file_id=None):
        _res = requests.get(f"{self._discovery_api}/file/{file_id}/", headers=self._jwt_header)
        if _res.status_code != 200:
            txt = _res.json() if _res.status_code < 500 else " "
            raise Exception(f"Some thing wrong, {txt}")
        meta = _res.json()
        try:
            response = self.client.get_object(bucket_name=bucket_name, object_name=meta['s3_key'])
        except Exception as e:
            raise e
        else:
            meta.update({
                'owner': meta['owner']['user']
            })
            meta = {key: value for key,value in meta.items() if key in ['owner', 'name', 'description', 'path', 'directory', 'human_size']}
            return meta, io.BytesIO(response.data)
        
    
    def read_ddf(self, file_id=None):
        _res = requests.get(f"{self._discovery_api}/file/{file_id}/", headers=self._jwt_header)
        check_http_status_code(_res)
        meta = _res.json()
        meta.update({
            'key': append_slash(meta['s3_key'])
        })
        _f_type = meta['type']['name']
        if _f_type == "parquet":
            return dd.read_parquet(f"s3://{bucket_name}/{meta['key']}", storage_options=self._storage_options)
        elif _f_type == "csv":
            return dd.read_csv(f"s3://{bucket_name}/{meta['key']}", storage_options=self._storage_options)
        elif _f_type == "sql-query":
            r = requests.get(f"{self._base_discovery_api}/api/v2/file/{meta['id']}/getSqlQuery/", headers=self._jwt_header)
            check_http_status_code(r)
            r = requests.get(f"{self._base_discovery_api}/api/sql/query/{r.json()['id']}/", headers=self._jwt_header)
            check_http_status_code(r)
            data = r.json()
            _database = DatabaseManagement(token=self.token)
            meta, schema = _database.get_table_schema(table_id=data['table'])
            exec(f"""
{schema}
from sqlalchemy import sql
{data['query']}
            """, globals())
            return _database.read_sql_query(table_id=data['table'], query_function=query, pk_column=data['pk_column'])
        return Exception(f"Can not read file extension {_f_type}, support [parquet, csv]")
        
    def read_df(self, file_id=None):
        _res = requests.get(f"{self._discovery_api}/file/{file_id}/", headers=self._jwt_header)
        if _res.status_code != 200:
            txt = _res.json() if _res.status_code < 500 else " "
            raise Exception(f"Some thing wrong, {txt}")
        meta = _res.json()
        meta.update({
            'key': append_slash(meta['s3_key'])
        })
        _f_type = meta['type']['name']
        if _f_type == "parquet":
            return pd.read_parquet(f"s3://{bucket_name}/{meta['key']}", storage_options=self._storage_options)
        elif _f_type == "csv":
            return pd.read_csv(f"s3://{bucket_name}/{meta['key']}", storage_options=self._storage_options)
        return Exception(f"Can not read file extension {_f_type}, support [parquet, csv]")
    
    
class DatabaseManagement(Base):
    def _get_connection_str(self, con_id=None):
        '''Get sqlalchemy connection string
        
        Args:
        ...
        '''
        if type(con_id) != int:
            raise Exception(f"Expect `con_id`=<int> but got {type(con_id)}, please input `con_id` eg con_id=0")
        r = requests.get(f"{self._base_discovery_api}/api/sql/database/{con_id}/", headers=self._jwt_header)
        if r.status_code > 500:
            return r.content
        elif r.status_code >= 400:
            return r.json()
        data = r.json()
        if 'sqlalchemy_uri' in data:
            return data['sqlalchemy_uri']
        return f"Some thing wrong!, {data}"
    
    def get_table_schema(self, table_id=None):
        '''Get table schema for sqlalchemy from table_id
        
        Args:
        ...
        '''
        
        if type(table_id) != int:
            raise Exception(f"Expect `table_id`=<int> but got {type(table_id)}, please input `table_id` eg table_id=0")
        r = requests.get(f"{self._base_discovery_api}/api/sql/table/{table_id}/", headers=self._jwt_header)
        if r.status_code > 500:
            return r.content, ""
        elif r.status_code >= 400:
            return r.json(), ""
        meta = r.json()
        schema = meta.pop('schema_code')
        return meta, schema


    def check_permission(self, con_id, table, column):
        '''Check table and column accesing permission from con_id
        
        Args:
        ...
        '''
        pass


    def check_query_permission(self, query, con_id):
        '''Check table and column accesing permission from sqlalchemy query   
        
        Args:
        ...
        '''
        for column in query.column_descriptions:
            table_name = column['expr'].table.name
            
            # check permission by using column['name'] and table_name
            if not self.check_permission(con_id=con_id, table=table_name, column=column['name']):
                raise Exception(f"You don't have permission in table={table_name}, column={column['name']}")  
            
    def write_sql_query(self, query_function=None, directory_id=None, table_id=None, pk_column=None, name=None, desciption=None, *args, **kwargs):
        '''Write sql_connection in pickle with checking permission
        
        Args:
        ...
        '''
        
        if query_function is None or inspect.isfunction(query_function)==False:
            raise Exception(f"Expect `query`=<function> but got {type(query_function)}, please input `query`")
        
        if directory_id == None or type(directory_id) != int:
            raise Exception(f"Please input data `directory`=<int>, but got {type(directory_id)} eg directory_id=0")
        
        if table_id == None or type(table_id) != int:
            raise Exception(f"Please input data `table_id`=<int>, but got {type(table_id)} eg table_id=0")
        
        if pk_column == None or type(pk_column) != str:
            raise Exception(f"Please input data `con_id`=<str>, but got {type(pk_column)} eg pk_column='id' ")
        
        if name == None or type(name) != str:
            raise Exception(f"Please input data `name`=<str>, but got {type(name)} eg name='myData' ")
        
        if desciption == None:
            desciption = f"query of {name}"
        
        _replace = self._check_fileExists(directory=directory_id, name=name)
        
        r = requests.post(f"{self._base_discovery_api}/api/sql/query/", headers=self._jwt_header,
                          json={
                                "directory": directory_id,
                                "table": table_id,
                                "name": name,
                                "description": desciption,
                                "pk_column": pk_column,
                                "query": inspect.getsource(query_function),
                                "replace": _replace
                          }
        )
        return r.json() if r.status_code < 500 else r.content
        
    def read_sql_query(self, table_id=None, query_function=None, pk_column=None):
        if table_id == None or type(table_id) != int:
            raise Exception(f"Please input data `table_id`=<int>, but got {type(table_id)} eg table_id=0")
        
        if query_function is None or inspect.isfunction(query_function) == False:
            raise Exception(f"Expect `query`=<function> but got {type(query_function)}, please input `query`")
        
        if pk_column == None or type(pk_column) != str:
            raise Exception(f"Please input data `con_id`=<str>, but got {type(pk_column)} eg pk_column='id' ")
        meta, schema = self.get_table_schema(table_id=table_id)
        con_str = self._get_connection_str(con_id=meta['database'])
        return dd.read_sql_query(sql=query_function(), con=con_str, index_col=pk_column)