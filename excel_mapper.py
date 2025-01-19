import pandas as pd
import json
import re


class ExcelMapper:
    def __init__(self, filepath):
        self.filepath = filepath
        self.dataframe = None

    def load_excel(self, sheet_name=0):
        try:
            self.dataframe = pd.read_excel(
                self.filepath, sheet_name=sheet_name, engine="openpyxl"
            )
        except Exception as e:
            raise ValueError(f"Failed to load the Excel file. Error: {e}")

    def map_headings(self, chapel_label="CHAPEL"):
        if self.dataframe is None:
            raise ValueError("Load an Excel file before mapping headings.")

        df = self.dataframe.copy()
        output = []

        # Room column: Always assumed to be the first column
        room_col = 0

        # Detect all day-date rows
        day_date_rows = self._find_rows_by_pattern(
            df, r"^[A-Za-z]+\s\d{2}/\d{2}/\d{2}$"
        )
        if not day_date_rows:
            raise ValueError("No day-date rows detected in the Excel file.")

        # Ensure we have time rows directly below the day-date rows
        time_rows = [row + 1 for row in day_date_rows if row + 1 < len(df)]

        if not time_rows:
            raise ValueError("No corresponding time rows found.")

        # Map each day-date to its column range
        day_date_map = self._map_day_date_columns(df, day_date_rows)

        # Process each room and generate timetable entries
        for i in range(len(df)):
            room = (
                str(df.iloc[i, room_col]).strip()
                if pd.notna(df.iloc[i, room_col])
                else None
            )
            if not room or room.lower() == chapel_label.lower():
                continue

            # Traverse day-date regions and extract data
            for (start_col, end_col), (day, date) in day_date_map.items():
                valid_columns = list(range(start_col, end_col + 1))

                # Assign time based on the detected time rows
                times = [
                    self._format_time(df.iloc[time_row, col])
                    for time_row in time_rows
                    for col in valid_columns
                ]

                # Process unit codes in the timetable and match them with time
                for col_idx, unit_code in enumerate(df.iloc[i, valid_columns].tolist()):
                    unit_code = str(unit_code).strip() if pd.notna(unit_code) else None
                    if unit_code and unit_code != chapel_label:
                        output.append(
                            {
                                "room": room,
                                "day": day,
                                "date": date,
                                "time": times[col_idx % len(times)],
                                "unit_code": unit_code.replace(" ", ""),
                            }
                        )

        return output

    @staticmethod
    def _find_rows_by_pattern(df, pattern):
        rows = []
        regex = re.compile(pattern)
        for i in range(len(df)):
            if any(
                isinstance(cell, str) and regex.match(cell.strip())
                for cell in df.iloc[i]
            ):
                rows.append(i)
        return rows

    @staticmethod
    def _map_day_date_columns(df, day_date_rows):
        day_date_map = {}
        current_day_date = None
        current_start_col = None

        for row in day_date_rows:
            for col in range(len(df.columns)):
                cell = df.iloc[row, col]
                if isinstance(cell, str) and re.match(
                    r"^[A-Za-z]+\s\d{2}/\d{2}/\d{2}$", cell.strip()
                ):
                    if current_day_date is not None:
                        # Save the previous day-date mapping
                        day_date_map[(current_start_col, col - 1)] = current_day_date

                    # Parse the new day and date
                    parts = cell.strip().split(" ", 1)
                    current_day_date = (parts[0], parts[1] if len(parts) > 1 else "")
                    current_start_col = col

        # Add the last range if available
        if current_day_date is not None:
            day_date_map[(current_start_col, len(df.columns) - 1)] = current_day_date

        return day_date_map

    @staticmethod
    def _format_time(time_value):
        if pd.isna(time_value) or str(time_value).strip() == "":
            return ""
        if isinstance(time_value, pd.Timestamp):
            return time_value.strftime("%H:%M")
        return str(time_value).strip()

    def export_to_json(self, data, output_path):
        try:
            with open(output_path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            raise ValueError(f"Failed to export data to JSON. Error: {e}")


# Example usage:
# filepath = "your_excel_file.xlsx"
# mapper = ExcelMapper(filepath)
# mapper.load_excel()
# timetable_data = mapper.map_headings()
# mapper.export_to_json(timetable_data, "output.json")
