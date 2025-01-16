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
        header_row=0,  # The header row that contains the day and date information
        time_row=1,  # The row that contains the times (second row in your case)
        room_col=0,  # The column that contains the room names
        chapel_label="CHAPEL",  # Label for rooms we want to skip
        day_columns={
            "Monday": (1, 3),  # Columns B-D
            "Tuesday": (4, 7),  # Columns E-H
            "Wednesday": (8, 10),  # Columns I-K
            "Thursday": (11, 14),  # Columns L-O
            "Friday": (15, 17),  # Columns P-R
        },
        excluded_columns=[4, 11],  # Exclude specific columns (1-based indices)
    ):
        """
        Map headings (room, day & date, time, and unit code) to a clean JSON format.
        """
        if self.dataframe is None:
            raise ValueError("Load an Excel file before mapping headings.")

        df = self.dataframe.copy()
        output = []
        day_date_columns = [1, 4, 8, 11, 15]  # Starting columns for each day

        # Loop through day columns to map data
        for day, (start_col, end_col) in day_columns.items():
            # Get valid columns (excluding the specified columns)
            valid_columns = [
                col
                for col in range(start_col, end_col + 1)
                if col + 1 not in excluded_columns
            ]

            # Get times for this day's columns (from the second row)
            times = []
            for col in valid_columns:
                time_value = df.iloc[time_row, col]
                print(
                    f"Checking time for {day} at column {col}: {time_value}"
                )  # Debug line
                if pd.isna(time_value) or str(time_value).strip() == "":
                    times.append("")  # If time is missing, add an empty string
                else:
                    # If it's a datetime, format it, otherwise keep as string
                    if isinstance(time_value, pd.Timestamp):
                        times.append(time_value.strftime("%H:%M"))
                    else:
                        # Handle time as a string, strip any surrounding spaces
                        times.append(str(time_value).strip())

            # Get day and date information
            full_day_date = None
            for col in day_date_columns:
                if col >= start_col and col <= end_col:
                    full_day_date = df.iloc[header_row, col]
                    break

            if isinstance(full_day_date, str):
                parts = full_day_date.split(" ", 1)
                day_part = parts[0]
                date_part = parts[1] if len(parts) > 1 else ""
            else:
                day_part, date_part = day, ""

            # Extract unit data
            for i in range(
                time_row + 1, len(df)
            ):  # Start extracting from the row after time
                room = df.iloc[i, room_col]
                room = str(room).strip() if pd.notna(room) else None
                if not room or room == chapel_label:
                    continue

                # Map unit codes for the current day
                for col_idx, unit_code in enumerate(df.iloc[i, valid_columns].tolist()):
                    unit_code = str(unit_code).strip() if pd.notna(unit_code) else None
                    if (
                        unit_code
                        and unit_code != chapel_label
                        and times[col_idx] != chapel_label
                    ):
                        output.append(
                            {
                                "room": room,
                                "day": day_part,
                                "date": date_part,
                                "time": times[col_idx],
                                "unit_code": unit_code,
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


# Usage example
if __name__ == "__main__":
    filepath = "/home/waribu/workspace/myPython/myTimetable/FINAL_ EXAMINATION TIMETABLE -MAY 2024.xlsx"

    try:
        mapper = ExcelMapper(filepath)
        mapper.load_excel()
        cleaned_data = mapper.map_headings()
        mapper.export_to_json(cleaned_data, "output.json")
        print("Cleaned data successfully exported to output.json")
    except Exception as e:
        print(f"An error occurred: {e}")
