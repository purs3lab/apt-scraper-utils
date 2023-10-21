import json

class DebianPkgStats:
    def __init__(self, pkg_name) -> None:
        self.pkg_name = pkg_name
    
    def add_dependency_status(self, status: str):
        self.dependency_status = status
    
    def add_download_status(self, status:str):
        self.download_status = status
    
    def add_extract_status(self, status:str):
        self.extract_status = status
    
    def add_build_status(self, status:str):
        self.build_status = status
    
    def add_codeql_status(self, status:str):
        self.codeql_db_status = status
    
    def add_codeql_analysis_status(self, status:str):
        self.codeql_analysis_status = status
    
    def toJson(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__)