import re
import tkinter as tk
from tkinter import filedialog, messagebox

def filter_csv_export(log_file):
    with open(log_file, 'r') as file:
        log_data = file.readlines()

    export_actions = []
    details = []
    exclude_words = ["inizializza", "servizio", "OlyAccess"]

    for line in log_data:
        if "CSV Export" in line or "PDF Export" in line:
            export_actions.append(line.strip())
            exec_id = re.search(r'exec-\d+', line).group(0)
            timestamp = re.search(r'\d\d\d\d/\d\d/\d\d \d\d.\d\d.\d\d', line).group(0)

            for detail_line in log_data:
                if exec_id in detail_line and timestamp in detail_line:
                    if not any(word in detail_line for word in exclude_words):
                        details.append(detail_line.strip())

    return export_actions, details

def write_to_file(filename, export_actions, details):
    with open(filename, 'w') as file:
        file.write("Export Actions (CSV and PDF):\n")
        for action in export_actions:
            file.write(action + '\n')

        file.write("\nDetails:\n")
        for detail in details:
            file.write(detail + '\n')

def select_log_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Log files", "*.log")])
    return file_path

log_file = select_log_file()
output_file = "c:/TEMP/Exports.log"
export_actions, details = filter_csv_export(log_file)
write_to_file(output_file, export_actions, details)

message = f"Filtered CSV and PDF Export actions and details written to {output_file}"
print(message)

root = tk.Tk()
root.withdraw()
messagebox.showinfo("Results", message)
