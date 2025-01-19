# **Wesley: Timetable Data Mapper**

## **Overview**

**Wesley** is a Python-based application designed to parse and map timetable data from Excel sheets used to organize academic schedules. The application extracts room assignments, unit codes, time slots, and day-date information, ensuring that the data is structured for easy processing, storage, and analysis. Wesley also ensures that unit codes are mapped only to the relevant day-date and time slots, providing a more organized output.

### **Key Features**
- **Day-Date Mapping**: Automatically detects and maps day-date information to the corresponding columns and rows.
- **Room Coordination**: Identifies cells containing the word "ROOM" and outputs their coordinates.
- **Time and Unit Code Mapping**: Matches unit codes with corresponding times and dates, removing any extraneous spaces from unit codes.
- **Excel Division**: Divides Excel data into two sections, ensuring unit codes above the second day-date row do not get mapped to the rows below.
- **JSON Export**: Outputs the mapped data as a structured JSON file, making it easy to import into other applications or systems.

## **Installation**

### **Prerequisites**

Before running Wesley, ensure you have Python 3.x and the following libraries installed:

- `pandas`
- `openpyxl`

To install the required libraries, run:

```bash
pip install pandas openpyxl
```

## **Usage**

### 1. **Clone the Repository**

Clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/wesley.git
cd wesley
```

### 2. **Load Excel Data**

To load an Excel file and process the timetable data:

```python
from Wesley import ExcelMapper

# Initialize the ExcelMapper with the file path
mapper = ExcelMapper("path_to_your_excel_file.xlsx")

# Load the Excel sheet (if you want to load a specific sheet, provide its name or index)
mapper.load_excel(sheet_name=0)  # You can replace 0 with the sheet name or index
```

### 3. **Map Timetable Data**

To extract and map the timetable data, including day-date, times, and unit codes:

```python
# Perform the mapping of day-date and unit codes
timetable_data = mapper.map_headings(chapel_label="CHAPEL")

# Print the mapped timetable data
print(timetable_data)
```

### 4. **Export to JSON**

To export the mapped data into a JSON file:

```python
# Export mapped data to a JSON file
mapper.export_to_json(timetable_data, "output_timetable.json")
```

### 5. **Map Room Coordinates**

To map and print the coordinates of any cell containing the word "ROOM":

```python
# Map and print coordinates for cells containing the word "ROOM"
room_coordinates = mapper.map_room_coordinates()

# Print the coordinates
print("Room Coordinates:", room_coordinates)
```

## **Input Data Format**

The app expects an Excel sheet with the following general structure:

- **Day-Date Rows**: Rows containing a combination of day names and dates in the format `DAY XX/XX/XX`.
- **Time Rows**: Time slots are assumed to be directly below each day-date row.
- **Unit Codes**: Unit codes are represented under each corresponding time slot, mapped to rooms and times.

Example data:

| ROOM   | MON 01/01/25 | MON 01/01/25 | TUE 02/01/25 | TUE 02/01/25 |
|--------|--------------|--------------|--------------|--------------|
| Room 1 | MATH101      | ENG102       | BIO201       | CHEM101      |
| Room 2 | COMP202      | HIST303      | PHYS104      | MATH101      |

### **Output Data Format**

The output will be a list of dictionaries in JSON format:

```json
[
    {
        "room": "Room 1",
        "day": "MON",
        "date": "01/01/25",
        "time": "08:00",
        "unit_code": "MATH101"
    },
    {
        "room": "Room 2",
        "day": "MON",
        "date": "01/01/25",
        "time": "09:00",
        "unit_code": "ENG102"
    },
    ...
]
```

## **Contributing**

We welcome contributions to **Wesley**! If you have any ideas for improvements, bug fixes, or additional features, feel free to fork the repository and submit a pull request.

### Steps to Contribute:
1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Make your changes and commit them.
4. Open a pull request to merge your changes into the main repository.

## **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


### **End of README**

This README provides everything users need to understand how to use **Wesley**, including installation, usage, and contributing guidelines, along with special thanks to Wesley and Waribu for their support.
