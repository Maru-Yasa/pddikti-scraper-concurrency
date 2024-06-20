from pddiktipy import api
from pprint import pprint as p
import pandas as pd
from datetime import datetime
import requests, json
from requests.adapters import HTTPAdapter
from concurrent.futures import ThreadPoolExecutor, as_completed
import openpyxl, os, sys

class Logger:
    def __init__(self):
        self.current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.log_file_path = f'log-{datetime.now().strftime("%Y-%m-%d")}.txt'

    def log(self, text) -> None:
        text = f'[{self.current_datetime}] - {text}'
        print(text)
        with open(self.log_file_path, 'a') as log_file:
            log_file.write(f'{text}\n')

class ApiFrontEnd:
    def __init__(self):
        self.base_url = 'https://api-frontend.kemdikbud.go.id'
        self.logger = Logger()

    def get(self, url):
        self.logger.log(f"Hitting {url}")
        http = requests.Session()
        http.mount('https://', HTTPAdapter(max_retries=3))

        try:
            response = http.get(url, timeout=15)
        except requests.exceptions.Timeout:
            self.logger.log(f"Timeout hitting {url}")
            return None
        
        self.logger.log(f"{response.status_code} - {url}")
        if response.status_code != 200:
            return None
        return response.json()

    def get_all_prodi(self, id_sp):
        act = "v2/detail_pt_prodi"
        url = f"{self.base_url}/{act}/{id_sp}"
        return self.get(url)
    
    def get_detail_prodi(self, id_sp, kode_prodi):
        act = "detail_prodi"
        url = f"{self.base_url}/{act}/{id_sp}/{kode_prodi}"
        return self.get(url)

class PddiktiScrapper:
    def __init__(self):
        self.api = api()
        self.api_front = ApiFrontEnd()
        self.logger = Logger()

    def extract(self, data, key):
        try:
            return data[key]
        except:
            return ""

    def save_excel(self, file_path, data, remove_duplicates=True, subset=[]):
        df = pd.DataFrame(data)
        if remove_duplicates:
            df = df.drop_duplicates(subset=subset)
        df.to_excel(file_path, index=False)

    def append_to_excel(self, file_path, data):
        df = pd.DataFrame(data)
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                df.to_excel(writer, index=False, header=writer.sheets[writer.sheets.keys()[0]].max_row == 1, startrow=writer.sheets[writer.sheets.keys()[0]].max_row)
        except FileNotFoundError:
            df.to_excel(file_path, index=False)

    def append_to_csv(self, file_path, data):
        df = pd.DataFrame(data)
        header = not os.path.exists(file_path)
        df.to_csv(file_path, mode='a', index=False, header=header)

    def save_json(self, file_path, data):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def dump_all_univ(self, export=False):
        self.logger.log("Begin dumping all univ")
        data = self.api.dump_all_univ()
        self.logger.log(f"Got {len(data)} data")

        if export:
            self.logger.log("Begin exporting data univ")
            file_name = f'dump_univ_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.xlsx'
            self.save_excel(file_name, data, subset=['kode_pt', 'id_sp'])
            self.logger.log("Success exporting data univ")
        else:
            return data
        
    def convert_to_one_x_ratio(self, numerator, denominator):
        if numerator == 0:
            return f"1:-"

        x = denominator / numerator

        return f"1:{x:.2f}"

    def process_univ(self, univ, file_name):
        all_prodi = self.api_front.get_all_prodi(self.extract(univ, 'id_sp'))
        if all_prodi is None:
            return

        data_prodi = []
        for prodi in all_prodi:
            try:
                detail_prodi = self.api_front.get_detail_prodi(self.extract(prodi, 'id_sms'), "2023189898")
                raw_rasio_prodi = detail_prodi.get('rasio')

                if detail_prodi is not None and detail_prodi.get('detailumum'):
                    detail_prodi = detail_prodi['detailumum']
                else:
                    detail_prodi = {}
                    raw_rasio_prodi = {}

                rasio_prodi = {}
                for rasio in raw_rasio_prodi:
                    rasio_prodi[rasio['smt']] = self.convert_to_one_x_ratio(rasio['jmldosen'], rasio['jmlmhs'])

                data_prodi.append({
                    "nama_pt": self.extract(univ, 'nama_pt'),
                    "kode_pt": self.extract(univ, 'kode_pt'),
                    **detail_prodi,
                    # **rasio_prodi
                    # "kode_prodi": self.extract(prodi, 'kode_prodi'),
                    # "nama": self.extract(prodi, 'nm_lemb'),
                    # "status": self.extract(prodi, 'stat_prodi'),
                    # "jenjang": self.extract(prodi, 'jenjang'),
                    # "akreditasi": self.extract(prodi, 'akreditasi'),
                    # "email": self.extract(detail_prodi, 'email'),
                    # "telepon": self.extract(detail_prodi, 'no_tel'),
                    # "fax": self.extract(detail_prodi, 'no_fax'),
                })
            except Exception as e:
                self.logger.log(f"Error processing: {e}")
                continue

        # Append data to the Excel file
        self.append_to_csv(file_name, data_prodi)

    def get_all_univ_prodi_detail(self):
        self.logger.log("Begin getting all univ prodi detail")
        all_univ = pd.read_excel(sys.argv[1]).to_dict('records')
        
        file_name = f'dump_univ_prodi_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.process_univ, univ, file_name) for univ in all_univ]
            for future in as_completed(futures):
                future.result()

if __name__ == '__main__':
    scrapper = PddiktiScrapper()
    scrapper.get_all_univ_prodi_detail()