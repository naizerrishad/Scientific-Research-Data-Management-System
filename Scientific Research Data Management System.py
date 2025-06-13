import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import os
import math
import avro.schema
import avro.io
import io

class ExperimentManager:
    def __init__(self):
        self.entries_list = []

    def add_entry(self, experiment_name, date, name, data_points):
        self.entries_list.append({
            "experiment_name": experiment_name,
            "date": date,
            "researcher": name,
            "data_points": data_points
        })

    def view_entries(self):
        if len(self.entries_list) == 0:
            return "No entries available."
        else:
            result = ""
            for idx, entry in enumerate(self.entries_list):
                result += f"Entry {idx + 1}:\n"
                result += f"  Experiment Name: {entry['experiment_name']}\n"
                result += f"  Date: {entry['date']}\n"
                result += f"  Researcher: {entry['researcher']}\n"
                result += f"  Data Points: {entry['data_points']}\n"
                result += "-" * 40 + "\n"
            return result

    def analyze_data(self, name, choice):
        found = False
        result = ""
        for i in self.entries_list:
            if i["experiment_name"] == name:
                found = True
                data_points = i["data_points"]

                if choice == 1:
                    sum_of_data_points = sum(data_points)
                    average = sum_of_data_points / len(data_points)
                    result = f"The average of experiment data points is: {average}"
                elif choice == 2:
                    mean = sum(data_points) / len(data_points)
                    squared_diffs = [(x - mean) ** 2 for x in data_points]
                    variance = sum(squared_diffs) / len(data_points)
                    standard_deviation = math.sqrt(variance)
                    result = f"The standard deviation of experiment data points is: {standard_deviation}"
                elif choice == 3:
                    data_points.sort()
                    n = len(data_points)
                    middle_index = n // 2

                    if n % 2 == 0:
                        median = (data_points[middle_index - 1] + data_points[middle_index]) / 2
                    else:
                        median = data_points[middle_index]
                    result = f"The median of experiment data points is: {median}"
                else:
                    result = "Invalid choice."
                break
        if not found:
            result = "Experiment name not found."
        return result

    def load_entries_from_file(self, filename):
        try:
            schema_path = 'schema.json'
            schema = avro.schema.parse(open(schema_path, 'r').read())

            file = open(filename, 'rb')
            buffer = io.BytesIO(file.read())
            decoder = avro.io.BinaryDecoder(buffer)
            reader = avro.io.DatumReader(schema)

            while True:
                try:
                    entry = reader.read(decoder)
                    self.entries_list.append(entry)
                except EOFError:
                    break

            file.close()
            return "Entries loaded from file successfully."
        except FileNotFoundError:
            return "File not found."
        except avro.schema.SchemaParseException:
            return "Error parsing Avro schema."
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

    def save_entries_to_file(self, filename):
        try:
            schema_path = 'schema.json'
            schema = avro.schema.parse(open(schema_path, 'r').read())
            buffer = io.BytesIO()
            writer = avro.io.DatumWriter(schema)
            encoder = avro.io.BinaryEncoder(buffer)

            for entry in self.entries_list:
                writer.write(entry, encoder)

            file = open(filename, 'wb')
            file.write(buffer.getvalue())
            file.close()

            return "Data saved successfully!"
        except FileNotFoundError:
            return "File not found."
        except avro.schema.SchemaParseException:
            return "Error parsing Avro schema."
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

class GUI:
    def __init__(self, root):
        self.manager = ExperimentManager()
        self.root = root
        self.root.title("Experiment Manager")
        
        # Add Entry
        tk.Button(root, text="Add Entry", command=self.add_entry).pack(pady=10)
        # View Entries
        tk.Button(root, text="View Entries", command=self.view_entries).pack(pady=10)
        # Analyze Data
        tk.Button(root, text="Analyze Data", command=self.analyze_data).pack(pady=10)
        # Load Entries from File
        tk.Button(root, text="Load Entries from File", command=self.load_entries).pack(pady=10)
        # Save Entries to File
        tk.Button(root, text="Save Entries to File", command=self.save_entries).pack(pady=10)

    def add_entry(self):
        experiment_name = simpledialog.askstring("Input", "Enter experiment title:")
        date = simpledialog.askstring("Input", "Enter date of research (year):")
        name = simpledialog.askstring("Input", "Enter name of researcher:")
        
        num_data = simpledialog.askinteger("Input", "Enter the number of data points:")
        data_points = []
        for i in range(num_data):
            data_point = simpledialog.askfloat("Input", f"Enter data point {i+1}:")
            data_points.append(data_point)
        
        self.manager.add_entry(experiment_name, date, name, data_points)
        messagebox.showinfo("Info", "Entry added successfully!")

    def view_entries(self):
        entries = self.manager.view_entries()
        messagebox.showinfo("Entries", entries)
        
    def analyze_data(self):
        # GUI to select experiment and analyze data
        def perform_analysis(choice):
            if not hasattr(self, 'experiment'):
                messagebox.showerror("Error", "No experiment selected.")
                return
        
            data_points = self.experiment["data_points"]

            if choice == "Average":
                average = sum(data_points) / len(data_points)
                result = f"The average of the data points is: {average}"
            elif choice == "Standard Deviation":
                mean = sum(data_points) / len(data_points)
                squared_diffs = [(x - mean) ** 2 for x in data_points]
                variance = sum(squared_diffs) / len(data_points)
                standard_deviation = math.sqrt(variance)
                result = f"The standard deviation of the data points is: {standard_deviation}"
            elif choice == "Median":
                data_points.sort()
                n = len(data_points)
                middle_index = n // 2
                if n % 2 == 0:
                    median = (data_points[middle_index - 1] + data_points[middle_index]) / 2
                else:
                    median = data_points[middle_index]
                result = f"The median of the data points is: {median}"
            messagebox.showinfo("Analysis Result", result)

        def on_experiment_select():
            experiment_name = experiment_name_entry.get()
            for exp in self.manager.entries_list:
                if exp["experiment_name"] == experiment_name:
                    self.experiment = exp
                    analysis_frame.pack(pady=10)
                    return
            messagebox.showerror("Error", "Experiment name not found.")

        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Analyze Data")

        tk.Label(analysis_window, text="Enter the name of the experiment to analyze:").pack(pady=10)
        experiment_name_entry = tk.Entry(analysis_window)
        experiment_name_entry.pack(pady=10)
        tk.Button(analysis_window, text="Enter", command=on_experiment_select).pack(pady=10)

        # Frame for analysis options
        analysis_frame = tk.Frame(analysis_window)

        tk.Button(analysis_frame, text="Average", command=lambda: perform_analysis("Average")).pack(pady=5)
        tk.Button(analysis_frame, text="Standard Deviation", command=lambda: perform_analysis("Standard Deviation")).pack(pady=5)
        tk.Button(analysis_frame, text="Median", command=lambda: perform_analysis("Median")).pack(pady=5)


    def load_entries(self):
        filename = filedialog.askopenfilename(title="Select a file", filetypes=(("Avro files", "*.avro"), ("All files", "*.*")))
        if filename:
            result = self.manager.load_entries_from_file(filename)
            messagebox.showinfo("Info", result)

    def save_entries(self):
        filename = filedialog.asksaveasfilename(title="Save as", defaultextension=".avro", filetypes=(("Avro files", "*.avro"), ("All files", "*.*")))
        if filename:
            result = self.manager.save_entries_to_file(filename)
            messagebox.showinfo("Info", result)
    
def main():
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
