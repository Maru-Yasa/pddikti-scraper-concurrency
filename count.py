import pandas as pd
import sys

columns = ['nama_pt', 'kode_pt', 'npsn', 'stat_prodi', 'namapt', 'linkpt', 'kode_prodi','nm_lemb','namajenjang','tgl_berdiri','sk_selenggara','tgl_sk_selenggara','tgl_sk_akred_prodi','jln','kode_pos','no_tel','no_fax','email','website','deskripsi','visi','misi','kompetensi','capaian','akreditas','lintang','bujur','id_sms'
]
df = pd.read_csv(sys.argv[1], names=columns, low_memory=False)
df.drop(columns=['visi', 'misi', 'deskripsi', 'kompetensi', 'capaian', 'akreditas'], inplace=True)
df.to_excel("dump_univ_prodi_detail_umum.xlsx")

print(df.count())