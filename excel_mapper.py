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
        print(f"Room column position: Row 1 to {len(df)}, Column {room_col + 1}")

        # Detect all day-date rows
        day_date_rows = self._find_rows_by_pattern(
            df, r"^[A-Za-z]+\s\d{2}/\d{2}/\d{2}$"
        )
        if not day_date_rows:
            raise ValueError("No day-date rows detected in the Excel file.")

        for row in day_date_rows:
            print(
                f"Day-date row position: Row {row + 1}, Columns 1 to {len(df.columns)}"
            )

        # Determine time rows: Rows immediately below day-date rows
        time_rows = [row + 1 for row in day_date_rows if row + 1 < len(df)]
        for row in time_rows:
            print(f"Time row position: Row {row + 1}, Columns 2 to {len(df.columns)}")

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
                times = [
                    self._format_time(df.iloc[time_row, col])
                    for time_row in time_rows
                    for col in valid_columns
                ]

                for col_idx, unit_code in enumerate(df.iloc[i, valid_columns].tolist()):
                    unit_code = str(unit_code).strip() if pd.notna(unit_code) else None
                    if unit_code and unit_code != chapel_label:
                        output.append(
                            {
                                "room": room,
                                "day": day,
                                "date": date,
                                "time": times[col_idx % len(times)],
                                "unit_code": unit_code,
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
        previous_col = None
        for row in day_date_rows:
            for col in range(len(df.columns)):
                cell = df.iloc[row, col]
                if isinstance(cell, str) and re.match(
                    r"^[A-Za-z]+\s\d{2}/\d{2}/\d{2}$", cell.strip()
                ):
                    if previous_col is not None:
                        day_date_map[previous_col] = (day, date)
                    parts = cell.split(" ", 1)
                    day = parts[0]
                    date = parts[1] if len(parts) > 1 else ""
                    previous_col = (col, len(df.columns) - 1)

        if previous_col is not None:
            day_date_map[previous_col] = (day, date)

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
