import requests
from .base import  Base
from .utils.requests import check_http_status_code

class GenerateDatadict(Base):
    def generate_datadict(self, name=None, directory_id=None, file_ids=None):
        if name == None or type(name) != str:
            raise Exception(f"Please input data `name`=<str>, but got {type(name)}")
        name = name.replace('.','')
        if directory_id == None or type(directory_id) != int:
            raise Exception(f"Please input data `directory_id`=<int>, but got {type(directory_id)}")
        if file_ids == None or type(file_ids) != list:
            raise Exception(f"Please input data `file_ids`=[int, int, int], but got {type(file_ids)}")
        
        r = requests.post(f"{self._discovery_api}/data-dictionary/generateDatadictPdf/", 
                          headers=self._jwt_header,
                          json={
                            "token": self.token,
                            "name": name,
                            "dir_id": directory_id,
                            "file_ids": file_ids
                          }
        )
        check_http_status_code(response=r)
        return r.json()
        