import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import json


class TimetableGUI:
    def __init__(self, master, timetable_data):
        self.master = master
        self.master.title("Wesley")
        self.master.geometry("1000x700")  # Enlarged the window

        self.master.configure(bg="#f0f8ff")  # Light blue background

        # Timetable data (unit_code, room, day, time, date)
        self.timetable_data = timetable_data

        # Basket to store selected unit codes
        self.selected_units = []

        # Create Search Box to search for a unit code
        self.search_label = tk.Label(
            master, text="Enter Unit Code:", bg="#f0f8ff", font=("Arial", 12)
        )
        self.search_label.grid(row=0, column=0, padx=10, pady=10)

        self.search_entry = tk.Entry(master, width=20, font=("Arial", 12))
        self.search_entry.grid(row=0, column=1, padx=10, pady=10)

        self.search_button = tk.Button(
            master,
            text="Search",
            command=self.search_unit_code,
            bg="#4682b4",
            fg="white",
            font=("Arial", 12),
        )
        self.search_button.grid(row=0, column=2, padx=10, pady=10)

        # Display search results
        self.result_label = tk.Label(
            master, text="Unit Details:", bg="#f0f8ff", font=("Arial", 12)
        )
        self.result_label.grid(row=1, column=0, padx=10, pady=10)

        self.result_text = tk.Label(
            master,
            text="",
            width=70,
            height=5,
            relief="sunken",
            bg="#ffffff",
            font=("Courier", 10),
        )
        self.result_text.grid(row=1, column=1, columnspan=2, padx=10, pady=10)

        # Basket (Listbox to hold selected unit codes)
        self.basket_label = tk.Label(
            master, text="Basket:", bg="#f0f8ff", font=("Arial", 12)
        )
        self.basket_label.grid(row=2, column=0, padx=10, pady=10)

        self.basket_listbox = tk.Listbox(master, height=6, width=50, font=("Arial", 12))
        self.basket_listbox.grid(row=2, column=1, columnspan=2, padx=10, pady=10)

        # Add button to add unit to the basket
        self.add_button = tk.Button(
            master,
            text="Add to Basket",
            command=self.add_to_basket,
            bg="#32cd32",
            fg="white",
            font=("Arial", 12),
        )
        self.add_button.grid(row=3, column=0, padx=10, pady=10)

        # Remove button to remove unit from the basket
        self.remove_button = tk.Button(
            master,
            text="Remove from Basket",
            command=self.remove_from_basket,
            bg="#ff6347",
            fg="white",
            font=("Arial", 12),
        )
        self.remove_button.grid(row=3, column=1, padx=10, pady=10)

        # Submit button to generate timetable for selected units
        self.submit_button = tk.Button(
            master,
            text="Generate Timetable",
            command=self.generate_timetable,
            bg="#4682b4",
            fg="white",
            font=("Arial", 12),
        )
        self.submit_button.grid(row=4, column=0, padx=10, pady=10)

        # Table for displaying the timetable
        self.table_label = tk.Label(
            master, text="Timetable:", bg="#f0f8ff", font=("Arial", 12)
        )
        self.table_label.grid(row=5, column=0, padx=10, pady=10)

        self.tree = ttk.Treeview(
            master,
            columns=("unit_code", "day", "date", "time", "room"),
            show="headings",
        )
        self.tree.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

        self.tree.heading("unit_code", text="Unit Code")
        self.tree.heading("day", text="Day")
        self.tree.heading("date", text="Date")
        self.tree.heading("time", text="Time")
        self.tree.heading("room", text="Room")

        self.tree.column("unit_code", width=150)
        self.tree.column("day", width=150)
        self.tree.column("date", width=150)
        self.tree.column("time", width=150)
        self.tree.column("room", width=150)

        # Add delete functionality for timetable rows
        self.tree.bind("<Delete>", self.delete_timetable_row)

    def search_unit_code(self):
        unit_code = self.search_entry.get().strip()
        if not unit_code:
            messagebox.showerror("Input Error", "Please enter a unit code to search.")
            return

        # Search for the unit in the timetable data
        result = next(
            (item for item in self.timetable_data if item["unit_code"] == unit_code),
            None,
        )

        if result:
            result_text = (
                f"Unit Code: {result['unit_code']}\n"
                f"Day: {result['day']}\n"
                f"Date: {result['date']}\n"
                f"Time: {result['time']}\n"
                f"Room: {result['room']}"
            )
            self.result_text.config(text=result_text)
        else:
            self.result_text.config(text="Unit Code not found.")

    def add_to_basket(self):
        unit_code = self.search_entry.get().strip()
        if not unit_code:
            messagebox.showerror(
                "Input Error", "Please enter a unit code to add to the basket."
            )
            return

        # Add the unit code to the basket if not already present
        if unit_code not in self.selected_units:
            self.selected_units.append(unit_code)
            self.basket_listbox.insert(tk.END, unit_code)
        else:
            messagebox.showinfo("Basket", "Unit code is already in the basket.")

    def remove_from_basket(self):
        try:
            selected_index = self.basket_listbox.curselection()[0]
            selected_item = self.basket_listbox.get(selected_index)
            self.basket_listbox.delete(selected_index)
            self.selected_units.remove(selected_item)
        except IndexError:
            messagebox.showerror("Selection Error", "Please select a unit to remove.")

    def generate_timetable(self):
        selected_units = [unit for unit in self.selected_units]
        if not selected_units:
            messagebox.showerror(
                "Basket Empty",
                "No unit codes selected. Please add unit codes to the basket.",
            )
            return

        # Filter the timetable data to show only selected units
        filtered_data = [
            item for item in self.timetable_data if item["unit_code"] in selected_units
        ]

        # Clear the current table
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Populate the table with the filtered data
        for item in filtered_data:
            self.tree.insert(
                "",
                "end",
                values=(
                    item["unit_code"],
                    item["day"],
                    item["date"],
                    item["time"],
                    item["room"],
                ),
            )

    def delete_timetable_row(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.delete(selected_item)


# Main program
if __name__ == "__main__":
    # Load timetable data from a JSON file
    try:
        with open("output.json", "r") as file:
            timetable_data = json.load(file)
    except FileNotFoundError:
        messagebox.showerror("File Error", "File not found.")
        timetable_data = []

    root = tk.Tk()
    gui = TimetableGUI(root, timetable_data)
    root.mainloop()
