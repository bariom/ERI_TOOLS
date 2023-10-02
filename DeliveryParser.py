import pdfplumber
import re
import pyperclip
import tkinter as tk
from tkinter import filedialog, Text, Scrollbar, Button


def process_pdf():
    inputFile = filedialog.askopenfilename(title="Select a PDF file", filetypes=[("PDF files", "*.pdf")])
    if not inputFile:
        return

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
                lines = re.findall(r'repositories/(.*?)/ch/(.*?)\n', all_text)
                for repo, xmlObj in lines:
                    xmlObj = xmlObj.split('/')[-1]
                    output_str += f"{JiraNum}\t{ref_word}\t{xmlObj}\t\tmissing\t\t{repo}\t{livDate}\n"
            else:
                tables = page.extract_tables()
                for table in tables:
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
    text_widget.delete(1.0, tk.END)
    text_widget.insert(tk.END, output_str)


# Create a Tkinter window
root = tk.Tk()
root.title("PDF Processor")

# Create a Text Widget
text_widget = Text(root, wrap='none')
text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

# Create a Scrollbar
scrollbar = Scrollbar(root)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Configure Text Widget and Scrollbar
text_widget.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=text_widget.yview)

# Create a Button for File Dialog
button = Button(root, text="Open PDF", command=process_pdf)
button.pack()

root.mainloop()
