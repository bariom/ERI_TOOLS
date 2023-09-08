###############################################################
### This is the linux version used to package xml from jira ###
###############################################################
import os
import sys
import xml.etree.ElementTree as ET
import re
import shutil
import datetime

#import pdb

# Check if the correct number of command-line arguments are provided
if len(sys.argv) != 5:
    print("Usage: python script.py <DELIVERY_SUMMARY.xml> <local_destination> <delivery_mode> <client_version>")
    sys.exit(1)

# Get the command-line arguments
xml_file = sys.argv[1]
local_destination = sys.argv[2]
delivery_mode = sys.argv[3]
client_version = sys.argv[4]

###
# Definition section
# Function to check if 'Parametrics' label exists
def check_for_parametrics_label(root):
    for label in root.findall(".//LABELS/LABEL[@name='Parametrics']"):
        return True
    return False

# Function to check if there is an issue in REF starting with 'SWITCH-ERI' or 'FDBTAB-ERI'
def check_for_parametrics_refs(root):
    for ref in root.findall(".//REFERENCES/REF"):
        issue = ref.get("issue")
        if issue.startswith("SWITCH-ERI") or issue.startswith("FDBTAB-ERI"):
            return True
    return False

# Parse the DELIVERY_SUMMARY.xml file
try:
    tree = ET.parse(xml_file)
    root = tree.getroot()
except ET.ParseError as e:
    print("Error parsing XML:", e)
    sys.exit(1)

# Define the base remote path
base_remote_path = f"/minio/ERI/sources/svn/"

#Define a list of file names to copy
files_to_copy = [
    "tablesconfig.xml",
    "catalog.xml",
    "kinds.properties",
    "beans.properties",
    "business.type",
    "business.symbol",
    "business.fmt",
    "business.enum",
    "pickup.enum",  # Add "pickup.enum" to the list
]

# Create a datetime string for the error file
current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
package_log_file = os.path.join(local_destination, f"./logs/package{current_datetime}.txt")

###


# Open the package_log_file file in append mode
with open(package_log_file, "a") as packlog:
    packlog.write(f"Start packaging at {current_datetime}\n")

    # Iterate through the OBJECTS elements and find those with type="XML"
    for obj in root.findall(".//OBJECTS/OBJ[@type='XML']"):
        # Get the URL attribute value
        url = obj.get("url")

        # Extract the relevant part of the URL using regular expressions
        match = re.match(r"svn://[^/]+/(.*)", url)

        if match:
            # Get the path part of the URL
            url_path = match.group(1)

            # Split the URL path by "/"
            path_parts = url_path.split("/")

            # Find the index of "branches"
            branches_index = path_parts.index("branches")

            # Construct the target path starting from "branches"
            target_path = base_remote_path + "/".join(path_parts[branches_index:])

            # Construct the local destination path
            local_path = os.path.join(local_destination, "/".join(path_parts[branches_index:]))

            try:
                # Create the directory structure if it doesn't exist
                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                # Copy the source file to the local destination
                shutil.copy(target_path, local_path)

                print("Copied:", target_path, "to", local_path)
            except FileNotFoundError as e:
                # Handle the case where the file is not found
                packlog.write(f"File not found: {target_path}\n")
                print("File not found:", target_path)
        else:
            print("Invalid URL format for object:", obj.get("name"))

###
# Parametrics section
# Check if 'Parametrics' label exists and set the 'withParametrics' variable
withParametrics = check_for_parametrics_label(root)

# Check if there is an issue in REF starting with 'SWITCH-ERI' or 'FDBTAB-ERI'
withSpecificIssues = check_for_parametrics_refs(root)

# Check if either 'withParametrics' or 'withSpecificIssues' is True
if withParametrics or withSpecificIssues:
    # Implement your logic for the case when either 'Parametrics' label exists
    # or there are specific issues in REF starting with 'SWITCH-ERI' or 'FDBTAB-ERI'.
    print("FOUND 'Parametrics' label or there are specific Jira issues.")
    source_rfml_directory = os.path.join(base_remote_path, "branches", client_version,
                                    "std/core/xml/std-core-xml/ch/eri/core/access/dictionary/A00/rfml")
    local_rfml_path = os.path.join(local_destination, "branches", client_version, "std/core/xml/std-core-xml/ch/eri/core/access/dictionary/A00/rfml")

    # Check if the source directory exists before copying
    if os.path.exists(source_rfml_directory):
        destination_directory = local_rfml_path
        #pdb.set_trace()
        try:
            # Create the directory structure if it doesn't exist
            #os.makedirs(destination_directory, exist_ok=True)

            # To avoid errors in copytree, remove the dir if exists
            if os.path.exists(destination_directory):
                shutil.rmtree(destination_directory)

            # Copy the source directory and its contents to the local destination
            shutil.copytree(source_rfml_directory, destination_directory)

            print("Copied directory:", source_rfml_directory, "to", destination_directory)
        except Exception as e:
            # Handle any exceptions that may occur during the copy operation
            print("Error copying directory:", str(e))
    else:
        print("Source directory not found:", source_rfml_directory)

else:
    # Implement your logic for the case when neither 'Parametrics' label exists
    # nor there are specific issues in REF starting with 'SWITCH-ERI' or 'FDBTAB-ERI'.
    print("No 'Parametrics'")
    # Add your additional logic here for this case

# Function to recursively search for and copy files
def copy_files_from_directory(source_directory, destination_directory):
    for root, dirs, files in os.walk(source_directory):
        for file_name in files:
            if file_name in files_to_copy:
                source_file_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(source_file_path, source_directory)
                destination_file_path = os.path.join(destination_directory, relative_path)

                try:
                    # Create the destination directory structure if it doesn't exist
                    os.makedirs(os.path.dirname(destination_file_path), exist_ok=True)

                    # Copy the source file to the local destination
                    shutil.copy(source_file_path, destination_file_path)

                    print("Copied file:", source_file_path, "to", destination_file_path)
                except Exception as e:
                    # Handle any exceptions that may occur during the copy operation
                    print("Error copying file:", str(e))

# Call the function to copy the specified files from the source directory to the destination directory
source_directory = os.path.join(base_remote_path, "branches", client_version)
destination_directory = os.path.join(local_destination, "branches", client_version)
copy_files_from_directory(source_directory, destination_directory)
###


if delivery_mode == 'std':
    # Check if 'application_server' directory exists, and if it does, delete it
    application_server_directory = os.path.join(local_destination, "application_server")
    if os.path.exists(application_server_directory):
        shutil.rmtree(application_server_directory)

    # Define the source and destination directories for copying '-xml' directories
    source_directory = local_destination
    destination_directory = os.path.join(local_destination, "application_server", "repositories")
elif delivery_mode == 'od':
    # Check if 'UIResources' directory exists, and if it does, delete it
    UIResources_directory = os.path.join(local_destination, "UIResources")
    if os.path.exists(UIResources_directory):
        shutil.rmtree(UIResources_directory)

    # Define the source and destination directories for copying '-xml' directories
    source_directory = local_destination
    destination_directory = os.path.join(local_destination, "UIResources")
else:
    print("Invalid delivery mode. Supported modes are 'std' and 'od'. ==> PACKAGE NOT FORMATTED")
    with open(package_log_file, "a") as packlog:
        packlog.write("Invalid delivery mode. Supported modes are 'std' and 'od'. ==> PACKAGE NOT FORMATTED")
    sys.exit(1) # Exit the script with an error code

# Iterate through the source_directory to find directories containing '-xml'
for root, dirs, files in os.walk(source_directory):
    for directory in dirs:
        if '-xml' in directory:
            source_path = os.path.join(root, directory)

            #for Windows only
            #destination_path = os.path.join(destination_directory, directory)
            destination_path = destination_directory

            # Check if the destination directory already exists
            if not os.path.exists(destination_path):
                # Create the destination directory if it doesn't exist
                os.makedirs(destination_path)

            # Move the directory and its contents to the destination
            shutil.move(source_path, destination_path)

            print("Moved directory:", source_path, "to", destination_path)

# Remove the 'branches' directory after moving its contents
shutil.rmtree(os.path.join(local_destination, "branches"))

with open(package_log_file, "a") as packlog:
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    packlog.write(f"Finished packaging at {current_datetime}\n")


