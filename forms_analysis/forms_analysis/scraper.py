import logging
import os
import pandas as pd  # type: ignore


directory = "./tmp/forms-fid"
dfs = []
df = pd.DataFrame({})
for filename in os.listdir(directory):
    logging.warning(filename)
    if filename.endswith("xls"):
        excel_file = directory + "/" + filename
        df = pd.read_excel(excel_file, sheet_name=1, skiprows=2)
        df["Source Form"] = filename
        dfs.append(df)


logging.warning(dfs)

combined_df = pd.concat(dfs, ignore_index=True)
csv_file = "output.csv"
combined_df.to_csv(csv_file, index=False)
