import pandas as pd
import json
import re
from typing import List, Dict, Tuple, Optional, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExcelMapper:
    """
    A class to map Excel timetable data into structured JSON format.
    Handles day-date rows, time mapping, and room assignments.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.dataframe: Optional[pd.DataFrame] = None

    def load_excel(self, sheet_name: int = 0) -> None:
        """Load Excel file into a pandas DataFrame."""
        try:
            self.dataframe = pd.read_excel(
                self.filepath, sheet_name=sheet_name, engine="openpyxl"
            )
            logger.info(f"Successfully loaded Excel file: {self.filepath}")
            logger.info(f"Data shape: {self.dataframe.shape}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Excel file not found: {self.filepath}")
        except Exception as e:
            raise ValueError(f"Failed to load the Excel file. Error: {e}")

    def map_headings(self, chapel_label: str = "CHAPEL") -> List[Dict[str, Any]]:
        """
        Map Excel timetable data to structured format.
        
        Args:
            chapel_label: Label to identify and skip chapel entries
            
        Returns:
            List of dictionaries containing timetable entries
        """
        if self.dataframe is None:
            raise ValueError("Load an Excel file before mapping headings.")

        df = self.dataframe.copy()
        output = []

        # Room column: Always assumed to be the first column
        room_col = 0

        # Detect all day-date rows
        day_date_rows = self._find_rows_by_pattern(
            df, r"^[A-Za-z]+\s+\d{2}/\d{2}/\d{2,4}$"
        )
        if not day_date_rows:
            logger.warning("No day-date rows detected in the Excel file.")
            raise ValueError("No day-date rows detected in the Excel file.")

        logger.info(f"Found day-date rows at indices: {day_date_rows}")

        # Ensure we have time rows directly below the day-date rows
        time_rows = [row + 1 for row in day_date_rows if row + 1 < len(df)]

        if not time_rows:
            raise ValueError("No corresponding time rows found.")

        logger.info(f"Time rows at indices: {time_rows}")

        # Map each day-date to its column range
        day_date_map = self._map_day_date_columns(df, day_date_rows)
        logger.info(f"Day-date column mapping: {day_date_map}")

        # Identify data rows (exclude day-date rows, time rows, header rows, and empty rows)
        data_rows = self._identify_data_rows(df, day_date_rows, time_rows)
        logger.info(f"Data rows identified at indices: {data_rows}")

        # Process each data row and generate timetable entries
        rooms_processed = 0
        for i in data_rows:
            room = self._clean_cell_value(df.iloc[i, room_col])
            if not room or room.upper() == chapel_label.upper() or room.upper() == "ROOM":
                continue

            rooms_processed += 1
            logger.debug(f"Processing room: {room}")

            # Traverse day-date regions and extract data
            for (start_col, end_col), (day, date) in day_date_map.items():
                valid_columns = list(range(start_col, end_col + 1))

                # Get times for this day-date range
                times = self._extract_times_for_columns(df, time_rows, valid_columns)

                # Process unit codes in the timetable
                for col_idx, col in enumerate(valid_columns):
                    if col >= len(df.columns):
                        continue
                        
                    unit_code = self._clean_cell_value(df.iloc[i, col])
                    if unit_code and unit_code.upper() != chapel_label.upper() and not self._is_time_value(unit_code):
                        time_value = times[col_idx] if col_idx < len(times) else ""
                        
                        entry = {
                            "room": room,
                            "day": day,
                            "date": date,
                            "time": time_value,
                            "unit_code": unit_code.replace(" ", ""),
                        }
                        output.append(entry)
                        logger.debug(f"Added entry: {entry}")

        logger.info(f"Processed {rooms_processed} rooms, generated {len(output)} timetable entries")
        return output

    def _identify_data_rows(self, df: pd.DataFrame, day_date_rows: List[int], 
                           time_rows: List[int]) -> List[int]:
        """
        Identify rows that contain actual timetable data (not headers, day-dates, or times).
        """
        data_rows = []
        excluded_rows = set(day_date_rows + time_rows)
        
        for i in range(len(df)):
            # Skip excluded rows
            if i in excluded_rows:
                continue
                
            # Check if this row has meaningful room data
            room_value = self._clean_cell_value(df.iloc[i, 0])
            
            # Skip if no room value or if it's a header
            if not room_value or room_value.upper() in ["ROOM", "ROOMS"]:
                continue
                
            # Check if the row contains any non-empty cells beyond the room column
            has_data = False
            for col in range(1, len(df.columns)):
                cell_value = self._clean_cell_value(df.iloc[i, col])
                if cell_value:
                    has_data = True
                    break
                    
            if has_data:
                data_rows.append(i)
                
        return data_rows

    def _is_time_value(self, value: str) -> bool:
        """Check if a value appears to be a time value."""
        if not value:
            return False
            
        # Common time patterns
        time_patterns = [
            r"^\d{1,2}:\d{2}(AM|PM)?$",  # 9:00AM, 11:30PM, etc.
            r"^\d{1,2}:\d{2}(AM|PM)?-\d{1,2}:\d{2}(AM|PM)?$",  # 9:00AM-11:00AM
            r"^\d{1,2}\.\d{2}(AM|PM)?$",  # 9.00AM
            r"^\d{1,2}\.\d{2}(AM|PM)?-\d{1,2}\.\d{2}(AM|PM)?$",  # 9.00AM-11.00AM
        ]
        
        for pattern in time_patterns:
            if re.match(pattern, value.upper()):
                return True
                
        return False

    def _clean_cell_value(self, cell_value: Any) -> Optional[str]:
        """Clean and validate cell values."""
        if pd.isna(cell_value):
            return None
        
        cleaned = str(cell_value).strip()
        return cleaned if cleaned else None

    def _extract_times_for_columns(self, df: pd.DataFrame, time_rows: List[int], 
                                 columns: List[int]) -> List[str]:
        """Extract time values for specific columns from time rows."""
        times = []
        for col in columns:
            if col >= len(df.columns):
                times.append("")
                continue
                
            # Try to find time in any of the time rows for this column
            time_found = ""
            for time_row in time_rows:
                if time_row < len(df):
                    time_value = self._format_time(df.iloc[time_row, col])
                    if time_value:
                        time_found = time_value
                        break
            times.append(time_found)
        
        return times

    @staticmethod
    def _find_rows_by_pattern(df: pd.DataFrame, pattern: str) -> List[int]:
        """Find rows that contain cells matching the given regex pattern."""
        rows = []
        regex = re.compile(pattern)
        
        for i in range(len(df)):
            for cell in df.iloc[i]:
                if isinstance(cell, str) and regex.match(cell.strip()):
                    rows.append(i)
                    break  # Found one match in this row, move to next row
        
        return rows

    @staticmethod
    def _map_day_date_columns(df: pd.DataFrame, day_date_rows: List[int]) -> Dict[Tuple[int, int], Tuple[str, str]]:
        """Map column ranges to their corresponding day-date values."""
        day_date_map = {}
        
        for row in day_date_rows:
            current_day_date = None
            current_start_col = None

            for col in range(len(df.columns)):
                cell = df.iloc[row, col]
                if isinstance(cell, str) and re.match(r"^[A-Za-z]+\s+\d{2}/\d{2}/\d{2,4}$", cell.strip()):
                    # Save previous mapping if it exists
                    if current_day_date is not None and current_start_col is not None:
                        day_date_map[(current_start_col, col - 1)] = current_day_date

                    # Parse new day and date
                    parts = cell.strip().split(None, 1)  # Split on any whitespace
                    current_day_date = (parts[0], parts[1] if len(parts) > 1 else "")
                    current_start_col = col

            # Add the last range if available
            if current_day_date is not None and current_start_col is not None:
                day_date_map[(current_start_col, len(df.columns) - 1)] = current_day_date

        return day_date_map

    @staticmethod
    def _format_time(time_value: Any) -> str:
        """Format time values consistently."""
        if pd.isna(time_value) or str(time_value).strip() == "":
            return ""
        
        if isinstance(time_value, pd.Timestamp):
            return time_value.strftime("%H:%M")
        
        # Handle string time formats
        time_str = str(time_value).strip()
        
        # Return time ranges as-is if they match expected patterns
        if re.match(r"^\d{1,2}:\d{2}(AM|PM)?-\d{1,2}:\d{2}(AM|PM)?$", time_str.upper()):
            return time_str
            
        # Try to parse individual time formats
        time_patterns = [
            r"^(\d{1,2}):(\d{2})(AM|PM)?$",  # HH:MM or H:MM with optional AM/PM
            r"^(\d{1,2})\.(\d{2})(AM|PM)?$",  # HH.MM or H.MM with optional AM/PM
            r"^(\d{1,2})(\d{2})(AM|PM)?$"     # HHMM or HMM with optional AM/PM
        ]
        
        for pattern in time_patterns:
            match = re.match(pattern, time_str.upper())
            if match:
                hours, minutes = match.groups()[:2]
                suffix = match.groups()[2] if len(match.groups()) > 2 else ""
                formatted_time = f"{int(hours):02d}:{int(minutes):02d}"
                return formatted_time + (suffix if suffix else "")
        
        return time_str

    def export_to_json(self, data: List[Dict[str, Any]], output_path: str) -> None:
        """Export timetable data to JSON file."""
        try:
            with open(output_path, "w", encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info(f"Successfully exported {len(data)} entries to {output_path}")
        except Exception as e:
            raise ValueError(f"Failed to export data to JSON. Error: {e}")

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics about the loaded data."""
        if self.dataframe is None:
            return {"error": "No data loaded"}
        
        return {
            "rows": len(self.dataframe),
            "columns": len(self.dataframe.columns),
            "shape": self.dataframe.shape,
            "column_names": list(self.dataframe.columns),
            "memory_usage": self.dataframe.memory_usage(deep=True).sum()
        }


# Enhanced main script with better error handling
def main():
    """Main execution function with comprehensive error handling."""
    filepath = "exam2.xlsx"
    output_file = "output.json"

    try:
        # Initialize mapper
        mapper = ExcelMapper(filepath)
        
        # Load and validate Excel file
        mapper.load_excel()
        
        # Get data summary
        stats = mapper.get_summary_stats()
        logger.info(f"Data summary: {stats}")
        
        # Process timetable data
        cleaned_data = mapper.map_headings()
        
        # Export to JSON
        mapper.export_to_json(cleaned_data, output_file)
        
        # Display success message
        print(f"✓ Successfully processed {len(cleaned_data)} timetable entries")
        print(f"✓ Data exported to {output_file}")
        
        # Start GUI if timetable_gui module is available
        try:
            import tkinter as tk
            from timetable_gui import TimetableGUI
            
            root = tk.Tk()
            gui = TimetableGUI(root, cleaned_data)
            root.mainloop()
            
        except ImportError:
            logger.warning("TimetableGUI not available. Data processing completed without GUI.")
            
    except FileNotFoundError:
        logger.error(f"Excel file not found: {filepath}")
        print(f"❌ Error: {filepath} not found. Please check the file path.")
        
    except ValueError as ve:
        logger.error(f"Data processing error: {ve}")
        print(f"❌ Data Error: {ve}")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected Error: {e}")


if __name__ == "__main__":
    main()