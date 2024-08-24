import csv

file_path = "Timetable.csv"

# Read the CSV file
with open(file_path, newline='') as csvfile:
    reader = csv.reader(csvfile)
    data = list(reader)

# Extract headers
dates = data[1]
times = data[2]

# Combine dates and times to create multi-level columns
columns = []
for i in range(len(dates)):
    if dates[i] and times[i]:
        columns.append(f"{dates[i]} {times[i]}")
    elif dates[i]:
        columns.append(dates[i])
    elif times[i]:
        columns.append(times[i])
    else:
        columns.append("")

# Create a list of dictionaries for rows with non-empty values
cleaned_data = []
for row in data[3:]:
    row_dict = {columns[i]: row[i] for i in range(len(row)) if row[i]}
    if row_dict:
        cleaned_data.append(row_dict)

# Print the cleaned timetable
for row in cleaned_data:
    print(row)
