import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import json
from typing import List, Dict, Any, Optional
from collections import defaultdict
import re


class TimetableGUI:
    def __init__(self, master, timetable_data):
        self.master = master
        self.master.title("Timetable Generator")
        self.master.geometry("1200x800")
        self.master.configure(bg="#f0f8ff")
        
        # Make window resizable
        self.master.rowconfigure(6, weight=1)
        self.master.columnconfigure(2, weight=1)

        # Timetable data
        self.timetable_data = timetable_data
        self.selected_units = []
        self.current_search_result = None
        
        # Get all unique unit codes for autocomplete
        self.all_unit_codes = list(set(item["unit_code"] for item in self.timetable_data))
        self.all_unit_codes.sort()

        self.setup_ui()
        self.setup_bindings()

    def setup_ui(self):
        """Set up the user interface components."""
        # Title
        title_label = tk.Label(
            self.master, 
            text="Timetable Generator", 
            bg="#f0f8ff", 
            font=("Arial", 16, "bold"),
            fg="#2c3e50"
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=10)

        # Search Frame
        search_frame = tk.Frame(self.master, bg="#f0f8ff")
        search_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Search components
        tk.Label(search_frame, text="Enter Unit Code:", bg="#f0f8ff", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        
        self.search_entry = tk.Entry(search_frame, width=20, font=("Arial", 12))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        # Autocomplete listbox (initially hidden)
        self.autocomplete_listbox = tk.Listbox(
            self.master, height=5, width=20, font=("Arial", 10)
        )
        self.autocomplete_visible = False

        self.search_button = tk.Button(
            search_frame, text="Search", command=self.search_unit_code,
            bg="#3498db", fg="white", font=("Arial", 12)
        )
        self.search_button.pack(side=tk.LEFT, padx=5)

        self.clear_search_button = tk.Button(
            search_frame, text="Clear", command=self.clear_search,
            bg="#95a5a6", fg="white", font=("Arial", 12)
        )
        self.clear_search_button.pack(side=tk.LEFT, padx=5)

        # Search results
        result_frame = tk.Frame(self.master, bg="#f0f8ff")
        result_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        tk.Label(result_frame, text="Unit Details:", bg="#f0f8ff", font=("Arial", 12, "bold")).pack(anchor="w")
        
        self.result_text = tk.Text(
            result_frame, width=80, height=6, relief="sunken",
            bg="#ffffff", font=("Courier", 10), state="disabled"
        )
        self.result_text.pack(fill="x", pady=5)

        # Basket frame
        basket_frame = tk.Frame(self.master, bg="#f0f8ff")
        basket_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        tk.Label(basket_frame, text="Selected Units:", bg="#f0f8ff", font=("Arial", 12, "bold")).pack(anchor="w")
        
        # Basket with scrollbar
        basket_container = tk.Frame(basket_frame, bg="#f0f8ff")
        basket_container.pack(fill="x", pady=5)
        
        self.basket_listbox = tk.Listbox(basket_container, height=5, font=("Arial", 11))
        scrollbar = tk.Scrollbar(basket_container, orient="vertical")
        
        self.basket_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.basket_listbox.yview)
        
        self.basket_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Button frame
        button_frame = tk.Frame(self.master, bg="#f0f8ff")
        button_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        self.add_button = tk.Button(
            button_frame, text="Add to Basket", command=self.add_to_basket,
            bg="#27ae60", fg="white", font=("Arial", 12), width=15
        )
        self.add_button.pack(side="left", padx=5)

        self.remove_button = tk.Button(
            button_frame, text="Remove Selected", command=self.remove_from_basket,
            bg="#e74c3c", fg="white", font=("Arial", 12), width=15
        )
        self.remove_button.pack(side="left", padx=5)

        self.clear_basket_button = tk.Button(
            button_frame, text="Clear All", command=self.clear_basket,
            bg="#f39c12", fg="white", font=("Arial", 12), width=15
        )
        self.clear_basket_button.pack(side="left", padx=5)

        self.generate_button = tk.Button(
            button_frame, text="Generate Timetable", command=self.generate_timetable,
            bg="#8e44ad", fg="white", font=("Arial", 12, "bold"), width=18
        )
        self.generate_button.pack(side="left", padx=5)

        # Export buttons
        export_frame = tk.Frame(self.master, bg="#f0f8ff")
        export_frame.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

        self.export_json_button = tk.Button(
            export_frame, text="Export to JSON", command=self.export_to_json,
            bg="#34495e", fg="white", font=("Arial", 10)
        )
        self.export_json_button.pack(side="left", padx=5)

        self.export_csv_button = tk.Button(
            export_frame, text="Export to CSV", command=self.export_to_csv,
            bg="#34495e", fg="white", font=("Arial", 10)
        )
        self.export_csv_button.pack(side="left", padx=5)

        # Statistics label
        self.stats_label = tk.Label(
            export_frame, text="", bg="#f0f8ff", font=("Arial", 10), fg="#7f8c8d"
        )
        self.stats_label.pack(side="right", padx=5)

        # Timetable display
        table_frame = tk.Frame(self.master, bg="#f0f8ff")
        table_frame.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        table_frame.rowconfigure(1, weight=1)
        table_frame.columnconfigure(0, weight=1)

        tk.Label(table_frame, text="Generated Timetable:", bg="#f0f8ff", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w")

        # Treeview with scrollbars
        tree_container = tk.Frame(table_frame)
        tree_container.grid(row=1, column=0, sticky="nsew")
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            tree_container,
            columns=("unit_code", "day", "date", "time", "room"),
            show="headings",
            height=15
        )
        
        # Configure columns
        self.tree.heading("unit_code", text="Unit Code")
        self.tree.heading("day", text="Day")
        self.tree.heading("date", text="Date")
        self.tree.heading("time", text="Time")
        self.tree.heading("room", text="Room")

        self.tree.column("unit_code", width=120, anchor="center")
        self.tree.column("day", width=100, anchor="center")
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("time", width=80, anchor="center")
        self.tree.column("room", width=100, anchor="center")

        # Scrollbars for treeview
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Status bar
        self.status_bar = tk.Label(
            self.master, text="Ready", relief="sunken", anchor="w",
            bg="#ecf0f1", font=("Arial", 10)
        )
        self.status_bar.grid(row=7, column=0, columnspan=3, sticky="ew", padx=5, pady=2)

        # Update statistics
        self.update_statistics()

    def setup_bindings(self):
        """Set up event bindings."""
        # Search entry bindings
        self.search_entry.bind("<KeyRelease>", self.on_search_key_release)
        self.search_entry.bind("<Return>", lambda e: self.search_unit_code())
        self.search_entry.bind("<FocusOut>", self.hide_autocomplete)
        
        # Autocomplete listbox bindings
        self.autocomplete_listbox.bind("<Double-Button-1>", self.select_from_autocomplete)
        self.autocomplete_listbox.bind("<Return>", self.select_from_autocomplete)
        
        # Treeview bindings
        self.tree.bind("<Delete>", self.delete_timetable_row)
        self.tree.bind("<Double-Button-1>", self.on_treeview_double_click)
        
        # Basket bindings
        self.basket_listbox.bind("<Double-Button-1>", lambda e: self.remove_from_basket())

    def on_search_key_release(self, event):
        """Handle key release in search entry for autocomplete."""
        if event.keysym in ('Up', 'Down', 'Return', 'Tab'):
            return
            
        text = self.search_entry.get().strip().upper()
        
        if len(text) < 2:
            self.hide_autocomplete()
            return
            
        # Filter unit codes
        matches = [code for code in self.all_unit_codes if text in code.upper()]
        
        if matches:
            self.show_autocomplete(matches[:10])  # Show max 10 matches
        else:
            self.hide_autocomplete()

    def show_autocomplete(self, matches):
        """Show autocomplete suggestions."""
        if not self.autocomplete_visible:
            # Position autocomplete below search entry
            x = self.search_entry.winfo_x()
            y = self.search_entry.winfo_y() + self.search_entry.winfo_height()
            self.autocomplete_listbox.place(x=x, y=y+30)
            self.autocomplete_visible = True
        
        self.autocomplete_listbox.delete(0, tk.END)
        for match in matches:
            self.autocomplete_listbox.insert(tk.END, match)

    def hide_autocomplete(self, event=None):
        """Hide autocomplete suggestions."""
        if self.autocomplete_visible:
            self.autocomplete_listbox.place_forget()
            self.autocomplete_visible = False

    def select_from_autocomplete(self, event=None):
        """Select item from autocomplete."""
        try:
            selection = self.autocomplete_listbox.curselection()[0]
            selected_text = self.autocomplete_listbox.get(selection)
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, selected_text)
            self.hide_autocomplete()
            self.search_unit_code()
        except IndexError:
            pass

    def search_unit_code(self):
        """Search for a unit code in the timetable data."""
        unit_code = self.search_entry.get().strip().upper()
        if not unit_code:
            messagebox.showerror("Input Error", "Please enter a unit code to search.")
            return

        self.hide_autocomplete()

        # Find all instances of the unit code
        results = [item for item in self.timetable_data if item["unit_code"].upper() == unit_code]

        if results:
            self.current_search_result = results[0]
            self.display_search_results(results)
            self.status_bar.config(text=f"Found {len(results)} instance(s) of {unit_code}")
        else:
            self.current_search_result = None
            self.result_text.config(state="normal")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, f"Unit Code '{unit_code}' not found.")
            self.result_text.config(state="disabled")
            self.status_bar.config(text="Unit code not found")

    def display_search_results(self, results):
        """Display search results in the text widget."""
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        
        if len(results) == 1:
            result = results[0]
            text = (
                f"Unit Code: {result['unit_code']}\n"
                f"Day: {result['day']}\n"
                f"Date: {result['date']}\n"
                f"Time: {result['time']}\n"
                f"Room: {result['room']}"
            )
        else:
            text = f"Found {len(results)} instances of {results[0]['unit_code']}:\n\n"
            for i, result in enumerate(results, 1):
                text += (
                    f"{i}. {result['day']} {result['date']} at {result['time']} "
                    f"in Room {result['room']}\n"
                )
        
        self.result_text.insert(1.0, text)
        self.result_text.config(state="disabled")

    def clear_search(self):
        """Clear search entry and results."""
        self.search_entry.delete(0, tk.END)
        self.current_search_result = None
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state="disabled")
        self.hide_autocomplete()
        self.status_bar.config(text="Search cleared")

    def add_to_basket(self):
        """Add unit code to the basket."""
        unit_code = self.search_entry.get().strip().upper()
        if not unit_code:
            messagebox.showerror("Input Error", "Please enter a unit code to add to the basket.")
            return

        # Check if unit code exists
        if not any(item["unit_code"].upper() == unit_code for item in self.timetable_data):
            messagebox.showerror("Unit Not Found", f"Unit code '{unit_code}' not found in timetable data.")
            return

        if unit_code not in self.selected_units:
            self.selected_units.append(unit_code)
            self.basket_listbox.insert(tk.END, unit_code)
            self.status_bar.config(text=f"Added {unit_code} to basket")
            self.update_statistics()
        else:
            messagebox.showinfo("Already Added", "Unit code is already in the basket.")

    def remove_from_basket(self):
        """Remove selected unit from the basket."""
        try:
            selected_indices = self.basket_listbox.curselection()
            if not selected_indices:
                messagebox.showerror("Selection Error", "Please select a unit to remove.")
                return
            
            # Remove in reverse order to maintain indices
            for index in reversed(selected_indices):
                selected_item = self.basket_listbox.get(index)
                self.basket_listbox.delete(index)
                self.selected_units.remove(selected_item)
            
            self.status_bar.config(text="Removed selected units from basket")
            self.update_statistics()
            
        except (IndexError, ValueError):
            messagebox.showerror("Selection Error", "Please select a unit to remove.")

    def clear_basket(self):
        """Clear all items from the basket."""
        if self.selected_units:
            result = messagebox.askyesno("Clear Basket", "Are you sure you want to clear all units from the basket?")
            if result:
                self.selected_units.clear()
                self.basket_listbox.delete(0, tk.END)
                self.status_bar.config(text="Basket cleared")
                self.update_statistics()

    def generate_timetable(self):
        """Generate timetable for selected units."""
        if not self.selected_units:
            messagebox.showerror("Basket Empty", "No unit codes selected. Please add unit codes to the basket.")
            return

        # Filter the timetable data
        filtered_data = [
            item for item in self.timetable_data 
            if item["unit_code"].upper() in [unit.upper() for unit in self.selected_units]
        ]

        # Sort by day and time
        day_order = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 7}
        filtered_data.sort(key=lambda x: (
            day_order.get(x["day"], 8),
            x["time"],
            x["unit_code"]
        ))

        # Clear and populate the table
        for row in self.tree.get_children():
            self.tree.delete(row)

        for item in filtered_data:
            self.tree.insert("", "end", values=(
                item["unit_code"], item["day"], item["date"], item["time"], item["room"]
            ))

        self.status_bar.config(text=f"Generated timetable with {len(filtered_data)} entries")
        
        # Check for conflicts
        self.check_conflicts(filtered_data)

    def check_conflicts(self, data):
        """Check for scheduling conflicts."""
        conflicts = []
        time_slots = defaultdict(list)
        
        for item in data:
            key = (item["day"], item["time"])
            time_slots[key].append(item)
        
        for (day, time), items in time_slots.items():
            if len(items) > 1:
                units = [item["unit_code"] for item in items]
                conflicts.append(f"{day} at {time}: {', '.join(units)}")
        
        if conflicts:
            conflict_msg = "⚠️ Scheduling conflicts detected:\n\n" + "\n".join(conflicts)
            messagebox.showwarning("Scheduling Conflicts", conflict_msg)

    def delete_timetable_row(self, event):
        """Delete selected rows from timetable."""
        selected_items = self.tree.selection()
        if selected_items:
            for item in selected_items:
                self.tree.delete(item)
            self.status_bar.config(text="Deleted selected timetable entries")

    def on_treeview_double_click(self, event):
        """Handle double-click on treeview."""
        item = self.tree.selection()[0]
        values = self.tree.item(item, "values")
        if values:
            unit_code = values[0]
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, unit_code)
            self.search_unit_code()

    def export_to_json(self):
        """Export current timetable to JSON."""
        if not self.tree.get_children():
            messagebox.showerror("No Data", "No timetable data to export.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                data = []
                for child in self.tree.get_children():
                    values = self.tree.item(child, "values")
                    data.append({
                        "unit_code": values[0],
                        "day": values[1],
                        "date": values[2],
                        "time": values[3],
                        "room": values[4]
                    })
                
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                messagebox.showinfo("Export Successful", f"Timetable exported to {filename}")
                self.status_bar.config(text=f"Exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

    def export_to_csv(self):
        """Export current timetable to CSV."""
        if not self.tree.get_children():
            messagebox.showerror("No Data", "No timetable data to export.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                import csv
                with open(filename, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Unit Code", "Day", "Date", "Time", "Room"])
                    
                    for child in self.tree.get_children():
                        values = self.tree.item(child, "values")
                        writer.writerow(values)
                
                messagebox.showinfo("Export Successful", f"Timetable exported to {filename}")
                self.status_bar.config(text=f"Exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

    def update_statistics(self):
        """Update statistics display."""
        total_units = len(self.all_unit_codes)
        selected_count = len(self.selected_units)
        self.stats_label.config(text=f"Total Units: {total_units} | Selected: {selected_count}")


def main():
    """Main function to run the GUI."""
    # Load timetable data
    try:
        with open("output.json", "r", encoding="utf-8") as file:
            timetable_data = json.load(file)
    except FileNotFoundError:
        messagebox.showerror("File Error", "output.json file not found.")
        timetable_data = []
    except json.JSONDecodeError:
        messagebox.showerror("File Error", "Invalid JSON format in output.json.")
        timetable_data = []

    if not timetable_data:
        messagebox.showwarning("No Data", "No timetable data found. The application will run with empty data.")

    root = tk.Tk()
    gui = TimetableGUI(root, timetable_data)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()