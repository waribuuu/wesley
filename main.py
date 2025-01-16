import pandas as pd
import json


class ExcelMapper:
    def __init__(self, filepath):
        self.filepath = filepath
        self.dataframe = None

    def load_excel(self, sheet_name=0):
        """
        Load an Excel sheet into a DataFrame.
        """
        try:
            self.dataframe = pd.read_excel(
                self.filepath, sheet_name=sheet_name, engine="openpyxl"
            )
        except Exception as e:
            raise ValueError(f"Failed to load the Excel file. Error: {e}")

    def map_headings(
        self,
        header_row=1,
        time_row=2,
        room_col=0,
        chapel_label="CHAPEL",
        day_columns={
            "Monday": (1, 3),
            "Tuesday": (4, 7),
            "Wednesday": (8, 10),
            "Thursday": (11, 14),
            "Friday": (15, 17),
        },
    ):
        """
        Map headings (room, day & date, time, and unit code) to a clean JSON format.

        :param header_row: Row number containing the day and date.
        :param time_row: Row number containing the time (excluding the first column).
        :param room_col: Column number containing the room names.
        :param chapel_label: Label to exclude for unit codes (e.g., "CHAPEL").
        :param day_columns: Dictionary mapping days to column ranges (1-based index).
        :return: A cleaned JSON structure with the specified mappings.
        """
        if self.dataframe is None:
            raise ValueError("Load an Excel file before mapping headings.")

        df = self.dataframe.copy()

        # Initialize output
        output = []

        # Loop through day columns to map data
        for day, (start_col, end_col) in day_columns.items():
            # Extract day and date for this range
            day_date = (
                df.iloc[header_row, start_col : end_col + 1]
                .fillna("")
                .astype(str)
                .tolist()
            )

            # Extract time for this range
            time = (
                df.iloc[time_row, start_col : end_col + 1]
                .fillna("")
                .astype(str)
                .tolist()
            )

            # Extract unit data for this range
            for i in range(time_row + 1, len(df)):
                room = df.iloc[i, room_col]
                room = str(room).strip() if pd.notna(room) else None
                if not room or room == chapel_label:
                    continue  # Skip empty rooms or "CHAPEL"

                # Map unit codes for the current day
                for col_idx, unit_code in enumerate(
                    df.iloc[i, start_col : end_col + 1].tolist()
                ):
                    if pd.notna(unit_code) and str(unit_code).strip() != "":
                        output.append(
                            {
                                "room": room,
                                "day_date": day_date[col_idx],
                                "time": time[col_idx],
                                "unit_code": str(unit_code).strip(),
                            }
                        )

        return output

    def export_to_json(self, data, output_path):
        """
        Export the cleaned data to a JSON file.
        """
        try:
            with open(output_path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            raise ValueError(f"Failed to export data to JSON. Error: {e}")


# Filepath for the Excel file
filepath = "FINAL_ EXAMINATION TIMETABLE -MAY 2024.xlsx"

# Usage
try:
    mapper = ExcelMapper(filepath)
    mapper.load_excel()  # Load the Excel file
    cleaned_data = mapper.map_headings()  # Extract and clean the data
    mapper.export_to_json(cleaned_data, "output.json")  # Export to JSON file
    print("Cleaned data successfully exported to output.json")
except Exception as e:
    print(f"An error occurred: {e}")
