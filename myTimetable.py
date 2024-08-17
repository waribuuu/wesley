import os
import pandas as pd

file_path = "FINAL_ EXAMINATION TIMETABLE -MAY 2024.xls"
if os.path.exists(file_path):
    data = pd.read_excel(file_path)
else:
    print(f"File not found: {file_path}")

data = pd.read_excel("/home/waribu/myPython/myTimetable/FINAL_ EXAMINATION TIMETABLE -MAY 2024.xls")

# Drop rows with any blank cells
data = data.dropna(how='any')

print(data)