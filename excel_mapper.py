import pandas as pd
import json


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

    def map_headings(
        self,
        header_row=0,
        time_row=1,
        room_col=0,
        chapel_label="CHAPEL",
        day_columns=None,
        excluded_columns=None,
    ):
        if self.dataframe is None:
            raise ValueError("Load an Excel file before mapping headings.")

        if day_columns is None:
            day_columns = {
                "Monday": (1, 3),
                "Tuesday": (4, 7),
                "Wednesday": (8, 10),
                "Thursday": (11, 14),
                "Friday": (15, 17),
            }

        if excluded_columns is None:
            excluded_columns = [4, 11]

        df = self.dataframe.copy()
        output = []
        day_date_columns = [1, 4, 8, 11, 15]

        for day, (start_col, end_col) in day_columns.items():
            valid_columns = [
                col
                for col in range(start_col, end_col + 1)
                if col + 1 not in excluded_columns
            ]

            times = [self._format_time(df.iloc[time_row, col]) for col in valid_columns]

            full_day_date = self._extract_day_date(
                df, header_row, start_col, end_col, day_date_columns, day
            )

            for i in range(time_row + 1, len(df)):
                room = (
                    str(df.iloc[i, room_col]).strip()
                    if pd.notna(df.iloc[i, room_col])
                    else None
                )
                if not room or room == chapel_label:
                    continue

                for col_idx, unit_code in enumerate(df.iloc[i, valid_columns].tolist()):
                    unit_code = str(unit_code).strip() if pd.notna(unit_code) else None
                    if unit_code and unit_code != chapel_label:
                        output.append(
                            {
                                "room": room,
                                "day": full_day_date[0],
                                "date": full_day_date[1],
                                "time": times[col_idx],
                                "unit_code": unit_code,
                            }
                        )

        return output

    @staticmethod
    def _format_time(time_value):
        if pd.isna(time_value) or str(time_value).strip() == "":
            return ""
        if isinstance(time_value, pd.Timestamp):
            return time_value.strftime("%H:%M")
        return str(time_value).strip()

    @staticmethod
    def _extract_day_date(df, header_row, start_col, end_col, day_date_columns, day):
        for col in day_date_columns:
            if col >= start_col and col <= end_col:
                full_day_date = df.iloc[header_row, col]
                break
        else:
            return day, ""

        if isinstance(full_day_date, str):
            parts = full_day_date.split(" ", 1)
            return parts[0], parts[1] if len(parts) > 1 else ""
        return day, ""

    def export_to_json(self, data, output_path):
        try:
            with open(output_path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            raise ValueError(f"Failed to export data to JSON. Error: {e}")
