import time
import os
import re
import tkinter as tk
import sys
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread
from PIL import Image
import pystray

percorso_rete = "//gvasrvdplab.eri.local/@PACKAGES/"
pattern_bpson_lug = re.compile(r'^(BPSON-LUG|SDG-RSM)-\d+$')

# Configure logging to save notifications to a log file
logging.basicConfig(filename='notification.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class MonitorDirectoryHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            directory_name = event.src_path.split('/')[-1]
            if pattern_bpson_lug.match(directory_name):
                directory_name_wk = directory_name
                logging.info(f"Nuova directory creata: {directory_name}")
                subdirectory = event.src_path + "/application_server"
                if os.path.exists(subdirectory):
                    Thread(target=show_notification_message, args=(directory_name, True)).start()
                else:
                    Thread(target=show_notification_message, args=(directory_name, False)).start()

    def on_moved(self, event):
        if event.is_directory:
            new_directory_name = event.dest_path.split('/')[-1]
            subdirectory = event.dest_path + "/application_server"
            # Check if the folder is renamed to "BPSON-LUG-" or "SDG-RSM-"
            if pattern_bpson_lug.match(new_directory_name) or pattern_bpson_lug.match(new_directory_name):
                logging.info(f"Nuova directory creata: {new_directory_name}")
                if os.path.exists(subdirectory):
                    Thread(target=show_notification_message, args=(new_directory_name, True)).start()
                else:
                    Thread(target=show_notification_message, args=(new_directory_name, False)).start()


def show_notification_message(directory_name, with_resources):
    root = tk.Tk()
    root.withdraw()

    popup = tk.Toplevel(root)
    popup.title("Notifica Directory")
    popup.geometry("300x100")
    popup.resizable(False, False)

    message = f"È stato pacchettizzato un nuovo punto: {directory_name}"
    if with_resources:
        message += "\nPacchetto con risorse XML"
        logging.info(f"Pacchetto con risorse XML")
        color = "orange"
    else:
        message += "\nPacchetto solo COBOL"
        logging.info(f"Pacchetto solo COBOL")
        color = "cyan"

    label = tk.Label(popup, text=message, wraplength=250, font=("Arial", 12), bg=color, fg="black", padx=10, pady=10)
    label.pack()

    popup.attributes("-topmost", True)
    popup.focus_force()
    popup.grab_set()
    popup.mainloop()

def quit_program(icon, item):
    icon.stop()
    logging.info(f"Chiusura applicazione")
    os._exit(0)  # Exit the application

def open_log_file(icon, item):
    os.startfile('notification.log')


def clear_log_file(icon, item):
    with open('notification.log', 'w') as file:
        file.write('')
    logging.info(f"Log file cleared.")

def create_system_tray_icon():
    image = Image.open('c:/DEVTOOLS/python_icon.png')  # Load an image for the system tray icon
    menu = (pystray.MenuItem('Show Log', open_log_file),  # Add a 'Show Log' option to open the log file
            pystray.MenuItem('Clear log', clear_log_file),
            pystray.MenuItem('Quit', quit_program), )   # Add a 'Quit' option to the system tray icon
    icon = pystray.Icon("Directory Monitor", image, "Directory Monitor", menu)
    logging.info(f"Avvio applicazione")
    icon.run()


if __name__ == "__main__":
    event_handler = MonitorDirectoryHandler()
    observer = Observer()
    observer.schedule(event_handler, path=percorso_rete, recursive=False)
    observer.start()

    Thread(target=create_system_tray_icon).start()  # Start the system tray icon in a new thread

    try:
        while True:
            time.sleep(15)
    except (KeyboardInterrupt, SystemExit):
        observer.stop()

    observer.join()
