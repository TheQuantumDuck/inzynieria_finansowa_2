import pandas as pd

file = "Dane rynkowe do zadań v2.xlsx"

xls = pd.ExcelFile(file)
print(xls.sheet_names)
