import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import pyperclip

def rev_search(directory_path):
    path = os.path.join(directory_path, "application_server")
    outputList = ""
    try:
        os.chdir(path)
    except FileNotFoundError:
        print(f"Errore: Impossibile connettersi a {path}")
        return

    rev_pattern = r"\$Rev: (\d+)"

    for root, dirs, files in os.walk(".", topdown=True):
        # Exclude files with ".war" extension
        files = [file for file in files if not (file.endswith(".war") or file.endswith(".jasper") or file.endswith(".jrxml") or file.endswith(".png"))]

        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, "r") as f:
                content = f.read()
                matches = re.findall(rev_pattern, content)
                for match in matches:
                    directory = os.path.dirname(file_path).split("repositories\\")[1].split("\\", 1)[0]
                    filename = os.path.basename(file_path)
                    outputList += f"{filename}\t\t{match}\t\t{directory}\n"
                    print(f"{filename}\t{match}\t{directory}\n")

                pyperclip.copy(outputList)

# Create a Tkinter root window (it won't be displayed)
root = tk.Tk()
root.withdraw()  # Hide the root window

# Show the message to the user
messagebox.showinfo("Message", "Pick root dir: BPSON-LUG-####")

# Use filedialog to open a directory picker
directory_path = filedialog.askdirectory(title="Select a Directory")

if not directory_path:
    print("Directory selection canceled.")
else:
    # Esegui la ricerca utilizzando lo script Python
    rev_search(directory_path)
