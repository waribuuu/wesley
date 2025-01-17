import tkinter as tk
from tkinter import messagebox
from excel_mapper import ExcelMapper
from timetable_gui import TimetableGUI

if __name__ == "__main__":
    filepath = "exam.xlsx"

    try:
        # Load and process the Excel file
        mapper = ExcelMapper(filepath)
        mapper.load_excel()
        cleaned_data = mapper.map_headings()
        mapper.export_to_json(cleaned_data, "output.json")

        # Start the GUI
        root = tk.Tk()
        gui = TimetableGUI(root, cleaned_data)
        root.mainloop()

    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
    except Exception as e:
        messagebox.showerror("Application Error", str(e))
