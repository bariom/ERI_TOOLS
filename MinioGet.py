# Programma per recuperare in locale le risorse XML specificate
# Utile per recuperare ed installare velocemente su ambiente BPS
import os
import shutil
import tkinter as tk
from glob import glob

def search_resource():
    resources_listbox.delete(0, tk.END)  # Clear the listbox
    resource_name = resource_entry.get()
    base_paths = [
        '\\\\gvasrvdplab\\minio\\ERI\\sources\\svn\\branches\\A03\\std\\core\\xml',
        '\\\\gvasrvdplab\\minio\\ERI\\sources\\svn\\branches\\A03\\std\\module\\PMS\\xml',
        '\\\\gvasrvdplab\\minio\\ERI\\sources\\svn\\branches\\A03\\std\\module\\UIBOOTSTRAP\\xml',
    ]
    destination_path = 'c:/temp/MinioPackage/'

    for base_path in base_paths:
        for path, dirs, files in os.walk(base_path):
            for wildcard in glob(os.path.join(path, resource_name)):
                # Rebuild path
                relative_path = os.path.relpath(wildcard, base_path)
                new_path = os.path.join(destination_path, relative_path)
                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                shutil.copy(wildcard, new_path)
                resources_listbox.insert(tk.END, f"Resource {resource_name} copied to {new_path}")

# Create GUI
root = tk.Tk()
root.title("minioGet")

resource_label = tk.Label(root, text="Enter resource name:")
resource_label.pack()

resource_entry = tk.Entry(root)
resource_entry.pack()

search_button = tk.Button(root, text="Search", command=search_resource)
search_button.pack()

# Frame to hold Listbox and Scrollbar
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=1)

resources_listbox = tk.Listbox(frame, width=100, height=10)
resources_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

scrollbar = tk.Scrollbar(frame, orient="vertical", command=resources_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

resources_listbox.config(yscrollcommand=scrollbar.set)

# Make window resizable
root.resizable(True, True)

root.mainloop()
