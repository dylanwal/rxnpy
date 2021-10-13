import glob
import pandas as pd


def get_line(file_path):
    with open(file_path, "r") as file:
        while True:
            yield file.readline()


csv_files = glob.glob(r"C:\Users\nicep\Desktop\pubchem\chempub_list*.csv")
combined_csv = pd.concat([pd.read_csv(f, header=None) for f in csv_files])
combined_csv.to_csv(r"C:\Users\nicep\Desktop\pubchem\combined.csv", header=False, index=False, encoding='utf-8-sig')

