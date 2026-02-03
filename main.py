import tkinter as tk
from tkinter import messagebox, filedialog
from excel_mapper import ExcelMapper
from timetable_gui import TimetableGUI
import sys
import os

if __name__ == "__main__":
    # Determine filepath: command-line arg, file dialog, or default
    if len(sys.argv) > 1 and sys.argv[1] not in ["--select", "-s"]:
        # Use command-line argument as filepath
        filepath = sys.argv[1]
    elif len(sys.argv) > 1 and sys.argv[1] in ["--select", "-s"]:
        # Show file dialog when --select or -s flag is used
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(
            title="Select Timetable Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
            initialdir="."
        )
        if not filepath:
            messagebox.showinfo("No File Selected", "No file was selected. Exiting.")
            exit()
        root.destroy()
    else:
        # Use default file
        filepath = "exam2.xlsx"

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
