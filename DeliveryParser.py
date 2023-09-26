import pdfplumber
import re
import pyperclip
import tkinter as tk
from tkinter import filedialog, Text, Scrollbar

def process_pdf(inputFile):
    output_str = ""
    JiraNum = inputFile.split('/')[-1].split('_')[0]

    with pdfplumber.open(inputFile) as pdf:
        for page in pdf.pages:
            all_text = page.extract_text()

            match = re.search(r'ref:\s+(\w+)', all_text)
            matchDate = re.search(r'sent :\s+(\d{4}-\d{2}-\d{2})', all_text)

            if matchDate:
                livDate = matchDate.group(1)

            if match:
                ref_word = match.group(1)

            if ref_word.startswith("NC"):
                # Specific logic for NC deliveries
                lines = re.findall(r'repositories/(.*?)/ch/(.*?)\n', all_text)
                for repo, xmlObj in lines:
                    xmlObj = xmlObj.split('/')[-1]  # Extract the last part after the last "/"
                    output_str += f"{JiraNum}\t{ref_word}\t{xmlObj}\t\tmissing\t\t{repo}\t{livDate}\n"
            else:
                # Attempt to extract the table
                table = page.extract_table()

                if table:
                    for row in table[1:]:
                        if len(row) >= 5:
                            object_data = row[0].replace('\n', '') if row[0] else ''
                            type_data = row[1].replace('\n', '') if row[1] else ''
                            src_date = row[4].replace('\n', '') if row[4] else ''

                            if object_data:
                                output_str += f"{JiraNum}\t{ref_word}\t{object_data}\t{type_data}\t{src_date}\t\t\t{livDate}\n"

    pyperclip.copy(output_str)
    display_result(output_str)


def display_result(output_str):
    result_window = tk.Tk()
    result_window.title("Parsed Data")

    def on_closing():
        result_window.destroy()
        root.destroy()

    result_window.protocol("WM_DELETE_WINDOW", on_closing)

    text_widget = Text(result_window, wrap='none')
    text_widget.insert(tk.END, output_str)
    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    scrollbar = Scrollbar(result_window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_widget.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=text_widget.yview)

    result_window.mainloop()


# Create a Tkinter window
root = tk.Tk()
root.withdraw()  # Hide the main window

# Open file dialog
inputFile = filedialog.askopenfilename(title="Select a PDF file", filetypes=[("PDF files", "*.pdf")])

# Process the selected file
if inputFile:
    process_pdf(inputFile)
