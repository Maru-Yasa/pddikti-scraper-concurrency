import pandas as pd
import json, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from PSWC import Logger
from PSWC import ApiFrontEnd

class PddiktiScrapper:
    def __init__(self):
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

    def save_csv(self, file_path, data, remove_duplicates=True, subset=[]):
        df = pd.DataFrame(data)
        if remove_duplicates:
            df = df.drop_duplicates(subset=subset)
        df.to_csv(file_path, index=False)

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
        df.to_csv(file_path, 
                  mode='a', 
                  index=False, 
                  header=header,
                  index_label=[*data[0]]
                )

    def save_json(self, file_path, data):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def dump_all_univ(self, output=None,csv=True, excel=False, export=False):
        self.logger.log("Begin dumping all univ")
        data = self.api_front.get_all_univ()
        self.logger.log(f"Got {len(data)} data")

        if export:
            self.logger.log("Begin exporting data univ")
            file_name = output if output != None else f'results/dump_univ/dump_univ_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.'+"xlsx" if excel else "csv"

            if excel:
                self.save_excel(file_name, data, subset=['kode_pt', 'id_sp'])
            else:
                self.save_csv(file_name, data, subset=['kode_pt', 'id_sp'])
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
                    rasio_prodi[f"Rasio Dosen:Mahasiswa {rasio['smt']}"] = self.convert_to_one_x_ratio(rasio['jmldosen'], rasio['jmlmhs'])

                detail_prodi.update(rasio_prodi)
                data_prodi.append({
                    "nama_pt": self.extract(univ, 'nama_pt'),
                    "kode_pt": self.extract(univ, 'kode_pt'),
                    **detail_prodi
                })
            except Exception as e:
                self.logger.log(f"Error processing: {e}")
                continue
            
        self.append_to_csv(file_name, data_prodi)

    def get_all_univ_prodi_detail(self, output=None, max_workers=5):
        self.logger.log("Begin getting all univ prodi detail")

        all_univ = self.dump_all_univ(export=False)
        
        file_name = output if output != None else f'results/dump_univ_prodi/dump_univ_prodi_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.process_univ, univ, file_name) for univ in all_univ]
            for future in as_completed(futures):
                future.result()