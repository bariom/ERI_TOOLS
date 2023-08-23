import os
import shutil
import tkinter as tk
from configparser import ConfigParser
from tkinter import ttk, messagebox, Listbox, Scrollbar, END, Text, INSERT
from datetime import date

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Installatore pacchetti XML BPS")
        style = ttk.Style()
        style.configure('My.TEntry', borderwidth=2, relief="solid")

        style.theme_use('clam')  # Utilizza il tema 'clam' che è generalmente più moderno

        # Configura lo stile del button
        style.configure('TButton', font=("Arial", 12, "bold"), background='green', foreground="white")

        self.config = ConfigParser()

        # Utilizza ttk.Entry invece di tk.Entry
        self.package_path_value = tk.StringVar()
        self.liv_repository_path = tk.StringVar()
        self.pms_liv_repository_path = tk.StringVar()
        self.core_repository_path = tk.StringVar()
        self.bootstrap_liv_repository_path = tk.StringVar()
        self.backup_path = tk.StringVar()
        self.package_to_install = tk.StringVar()

        self.load_config()

        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(11, weight=1)

        tk.Label(root, text="Pacchetto da installare", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky='w')
        self.package_entry = ttk.Entry(root, textvariable=self.package_to_install, font=("Arial", 12), style='My.TEntry')
        self.package_entry.grid(row=0, column=1, sticky='ew')
        self.package_entry.insert(tk.END, "BPSON-LUG-")
        self.package_entry.grid(row=0, column=1, sticky='ew')

        self.analyze_button = ttk.Button(root, text="Analizza pacchetto", command=self.install_package)
        self.analyze_button.grid(row=1, column=0, columnspan=2)

        self.install_button = ttk.Button(root, text="Installa pacchetto", state=tk.DISABLED, command=self.continue_installation)

        tk.Label(root, text="Path pacchetti").grid(row=2, column=0, sticky='w')
        tk.Entry(root, textvariable=self.package_path_value).grid(row=2, column=1, sticky='ew')

        tk.Label(root, text="Path Liv Repository").grid(row=3, column=0, sticky='w')
        tk.Entry(root, textvariable=self.liv_repository_path).grid(row=3, column=1, sticky='ew')

        tk.Label(root, text="Path PMS Liv Repository").grid(row=4, column=0, sticky='w')
        tk.Entry(root, textvariable=self.pms_liv_repository_path).grid(row=4, column=1, sticky='ew')

        tk.Label(root, text="Path Bootstrap Liv Repository").grid(row=5, column=0, sticky='w')
        tk.Entry(root, textvariable=self.bootstrap_liv_repository_path).grid(row=5, column=1, sticky='ew')

        tk.Label(root, text="Path Repository Core").grid(row=6, column=0, sticky='w')
        tk.Entry(root, textvariable=self.core_repository_path).grid(row=6, column=1, sticky='ew')

        tk.Label(root, text="Percorso Backup").grid(row=7, column=0, sticky='w')
        tk.Entry(root, textvariable=self.backup_path).grid(row=7, column=1, sticky='ew')

        tk.Button(root, text="Salva configurazione", command=self.save_config).grid(row=8, column=0, columnspan=2)

        self.resource_listbox = Listbox(root)
        self.resource_listbox.grid(row=9, column=0, columnspan=2, sticky='nsew')

        self.resource_scrollbar = Scrollbar(root, command=self.resource_listbox.yview)
        self.resource_scrollbar.grid(row=9, column=2, sticky='ns')
        self.resource_listbox.config(yscrollcommand=self.resource_scrollbar.set)

        self.log_text = Text(root)
        self.log_text.grid(row=11, column=0, columnspan=3, sticky='nsew')

        self.log_scrollbar = Scrollbar(root, command=self.log_text.yview)
        self.log_scrollbar.grid(row=11, column=3, sticky='ns')
        self.log_text.config(yscrollcommand=self.log_scrollbar.set)

        root.geometry("750x550")  # Imposta la larghezza a 550 e l'altezza a 450
        root.resizable(True, True)  # Rendi la finestra ridimensionabile

    def load_config(self):
        if os.path.exists("installPackage.conf"):
            self.config.read("installPackage.conf")

            self.package_path_value.set(self.config.get('Paths', 'package_path', fallback=''))
            self.liv_repository_path.set(self.config.get('Paths', 'liv_repository_path', fallback=''))
            self.pms_liv_repository_path.set(self.config.get('Paths', 'pms_liv_repository_path', fallback=''))
            self.core_repository_path.set(self.config.get('Paths', 'core_repository_path', fallback=''))
            self.bootstrap_liv_repository_path.set(self.config.get('Paths', 'bootstrap_liv_repository_path', fallback=''))
            self.backup_path.set(self.config.get('Paths', 'backup_path', fallback=''))

    def save_config(self):
        self.config['Paths'] = {
            'package_path': self.package_path_value.get(),
            'liv_repository_path': self.liv_repository_path.get(),
            'pms_liv_repository_path': self.pms_liv_repository_path.get(),
            'core_repository_path': self.core_repository_path.get(),
            'bootstrap_liv_repository_path': self.bootstrap_liv_repository_path.get(),
            'backup_path': self.backup_path.get()
        }

        with open('installPackage.conf', 'w') as configfile:
            self.config.write(configfile)

        messagebox.showinfo("Successo", "Configurazione salvata con successo.")

    def install_package(self):
        package_name = self.package_to_install.get()

        if not package_name.startswith("BPSON-LUG"):
            messagebox.showerror("Errore", "Il nome del pacchetto deve iniziare con 'BPSON-LUG'.")
            return

        package_path = os.path.join(self.package_path_value.get(), package_name)

        if os.path.exists(package_path):
            resource_files = []
            repository_path = os.path.join(package_path, "application_server", "repositories")
            std_core_xml_path = os.path.join(repository_path, "std-core-xml")
            std_module_pms_xml_path = os.path.join(repository_path, "std-module-PMS-xml")
            std_module_bootstrap_xml_path = os.path.join(repository_path, "std-module-UIBOOTSTRAP-xml")

            if os.path.exists(std_core_xml_path):
                for root_dir, _, files in os.walk(std_core_xml_path):
                    for file in files:
                        resource_files.append(
                            (os.path.relpath(os.path.join(root_dir, file), std_core_xml_path), "std-core-xml")
                        )

            if os.path.exists(std_module_pms_xml_path):
                for root_dir, _, files in os.walk(std_module_pms_xml_path):
                    for file in files:
                        resource_files.append(
                            (os.path.relpath(os.path.join(root_dir, file), std_module_pms_xml_path), "std-module-PMS-xml")
                        )

            if os.path.exists(std_module_bootstrap_xml_path):
                for root_dir, _, files in os.walk(std_module_bootstrap_xml_path):
                    for file in files:
                        resource_files.append(
                            (os.path.relpath(os.path.join(root_dir, file), std_module_bootstrap_xml_path), "std-module-UIBOOTSTRAP-xml")
                        )

            self.resource_listbox.delete(0, END)
            for file, xml_type in resource_files:
                self.resource_listbox.insert(END, f"{file} ({xml_type})")

            messagebox.showinfo("Successo", "Lista delle risorse XML aggiornata.")
            self.install_button.config(state=tk.NORMAL)
            self.analyze_button.grid_remove()
            self.install_button.grid(row=1, column=0, columnspan=2)

            self.resource_files = resource_files
            self.package_path_value.set(package_path)

        else:
            messagebox.showerror("Errore", "Il pacchetto specificato non esiste.")

    def continue_installation(self):
        backup_folder_name = f"{date.today().strftime('%Y-%m-%d')}_{self.package_to_install.get()}"
        backup_folder = os.path.join(self.backup_path.get(), backup_folder_name)

        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        log = "Operazioni di backup:\n\n"
        error_flag = False
        for file, xml_type in self.resource_files:
            try:
                if xml_type == "std-core-xml":
                    source_file_path = os.path.join(self.liv_repository_path.get(), file)
                if xml_type == "std-module-PMS-xml":
                    source_file_path = os.path.join(self.pms_liv_repository_path.get(), file)
                if xml_type == "std-module-UIBOOTSTRAP-xml":
                    source_file_path = os.path.join(self.bootstrap_liv_repository_path.get(), file)

                target_file_path = os.path.join(backup_folder, file)

                target_directory = os.path.dirname(target_file_path)
                if not os.path.exists(target_directory):
                    os.makedirs(target_directory)

                shutil.copy(source_file_path, target_file_path)
                log += f"Copiato {file} in {target_file_path}\n"
            except FileNotFoundError:
                log += f"Il file {file} non esiste nel repository di delivery\n"
                error_flag = False

        log += "\nOperazioni di installazione:\n\n"

        liv_repository_path = self.liv_repository_path.get()
        pms_liv_repository_path = self.pms_liv_repository_path.get()
        bootstrap_liv_repository_path = self.bootstrap_liv_repository_path.get()

        for file, xml_type in self.resource_files:
            try:
                if xml_type == "std-core-xml":
                    source_file_path = os.path.join(os.path.join(self.package_path_value.get(), "application_server", "repositories",
                                                                 "std-core-xml"), file)
                    target_file_path = os.path.join(liv_repository_path, file)
                if xml_type == "std-module-PMS-xml":
                    source_file_path = os.path.join(os.path.join(self.package_path_value.get(), "application_server", "repositories",
                                                                 "std-module-PMS-xml"), file)
                    target_file_path = os.path.join(pms_liv_repository_path, file)
                if xml_type == "std-module-UIBOOTSTRAP-xml":
                    source_file_path = os.path.join(os.path.join(self.package_path_value.get(), "application_server", "repositories",
                                                                 "std-module-UIBOOTSTRAP-xml"), file)
                    target_file_path = os.path.join(bootstrap_liv_repository_path, file)

                target_directory = os.path.dirname(target_file_path)
                if not os.path.exists(target_directory):
                    os.makedirs(target_directory)

                shutil.copy(source_file_path, target_file_path)
                log += f"Copiato {file} in {target_file_path}\n"
            except FileNotFoundError:
                log += f"Il file {file} non esiste nel repository di delivery\n"
                error_flag = True

        self.log_text.delete(1.0, END)
        self.log_text.insert(INSERT, log)

        if not error_flag:
            messagebox.showinfo("Successo", "Pacchetto XML installato correttamente.\n\n*** CHIUDI L'APP PER CARICARE UN NUOVO PACCHETTO ***")
        else:
            messagebox.showwarning("Attenzione", "Si sono verificati errori durante l'installazione.")

        self.analyze_button.grid()
        self.install_button.grid_remove()





root = tk.Tk()
app = App(root)
root.mainloop()
