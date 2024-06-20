from PSWC import Logger
from PSWC import Helper
from requests.adapters import HTTPAdapter
import requests

class ApiFrontEnd:
    def __init__(self):
        self.base_url = 'https://api-frontend.kemdikbud.go.id'
        self.logger = Logger()
        self.helper = Helper()
    
    def get_all_univ(self):
        act = "loadpt"
        url = f"{self.base_url}/{act}"
        return self.helper.get(url)
    
    def get_all_prodi(self, id_sp):
        act = "v2/detail_pt_prodi"
        url = f"{self.base_url}/{act}/{id_sp}"
        return self.helper.get(url)
    
    def get_detail_prodi(self, id_sp, kode_prodi):
        act = "detail_prodi"
        url = f"{self.base_url}/{act}/{id_sp}/{kode_prodi}"
        return self.helper.get(url)
