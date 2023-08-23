import os
import json
import requests
import datetime

# Configuration settings
CONFIG = {
    "username": "deliverygva",
    "password": "jira28042020",
    "jira_base_url": "http://erijira03",
    "output_directory": "C:/TEMP/JIRA_packages",
    "excluded_projects": ["AUDI-GVA", "REPTRK-ERI", "ERIDEV-GVA", "SWITCH-ERI", "FDBTAB-ERI"]
}

# Set to keep track of visited issues to avoid duplicates
visited_issues = set()

# Function to retrieve issue data from Jira API
def get_issue_data(issue_key):
    api_url = f"{CONFIG['jira_base_url']}/rest/api/2/issue/{issue_key}/"
    response = requests.get(api_url, auth=(CONFIG['username'], CONFIG['password']))

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to retrieve issue {issue_key}. Status code: {response.status_code}")
        return None

# Function to recursively get linked issues and their custom field data
def get_recursive_linked_issues(issue_key, created_after, depth=0):
    if issue_key in visited_issues:
        return []

    visited_issues.add(issue_key)

    issue_data = get_issue_data(issue_key)
    if not issue_data:
        return []

    result = []

    # Fetch customfield_10330 data (Objects to deliver)
    custom_field_data = issue_data.get('fields', {}).get('customfield_10330', [])
    if custom_field_data:
        print("  " * depth + f"Resources for {issue_key}:")
        for custom_value in custom_field_data:
            print("  " * (depth + 1) + custom_value)

    linked_issues = issue_data.get('fields', {}).get('issuelinks', [])
    if not linked_issues:
        return []

    for linked_issue in linked_issues:
        if 'outwardIssue' in linked_issue:
            linked_issue_key = linked_issue['outwardIssue']['key']
            if linked_issue_key not in visited_issues:
                linked_issue_data = get_issue_data(linked_issue_key)
                if linked_issue_data:
                    # Check if the project is excluded
                    project_key = linked_issue_data.get('fields', {}).get('project', {}).get('key', '').strip()
                    if project_key in (key.strip() for key in CONFIG['excluded_projects']):
                        continue

                    # Check the "versions" field
                    versions_field = linked_issue_data.get('fields', {}).get('versions', [])
                    if not any(version.get('name') == 'A03' for version in versions_field):
                        continue

                    # Check the created date
                    created_date_str = linked_issue_data.get('fields', {}).get('created')
                    if created_date_str:
                        created_date = datetime.datetime.strptime(created_date_str, '%Y-%m-%dT%H:%M:%S.%f%z').date()
                        if created_date < created_after:
                            continue

                    result.append((linked_issue_key, depth))
                    result.extend(get_recursive_linked_issues(linked_issue_key, created_after, depth + 1))

        if 'inwardIssue' in linked_issue:
            linked_issue_key = linked_issue['inwardIssue']['key']
            if linked_issue_key not in visited_issues:
                linked_issue_data = get_issue_data(linked_issue_key)
                if linked_issue_data:
                    # Check if the project is excluded
                    project_key = linked_issue_data.get('fields', {}).get('project', {}).get('key', '').strip()
                    if project_key in (key.strip() for key in CONFIG['excluded_projects']):
                        continue

                    # Check the "versions" field
                    versions_field = linked_issue_data.get('fields', {}).get('versions', [])
                    if not any(version.get('name') == 'A03' for version in versions_field):
                        continue

                    # Check the created date
                    created_date_str = linked_issue_data.get('fields', {}).get('created')
                    if created_date_str:
                        created_date = datetime.datetime.strptime(created_date_str, '%Y-%m-%dT%H:%M:%S.%f%z').date()
                        if created_date < created_after:
                            continue

                    result.append((linked_issue_key, depth))
                    result.extend(get_recursive_linked_issues(linked_issue_key, created_after, depth + 1))

    return result


if __name__ == "__main__":
    # Input issue key and date to skip issues created before
    issue_key = input("Enter the issue key: ")
    created_after = input("Enter the date (YYYY-MM-DD) to skip issues created before: ")

    try:
        created_after_date = datetime.datetime.strptime(created_after, '%Y-%m-%d').date()
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        exit(1)

    # Get linked issues and custom field data
    linked_issues = get_recursive_linked_issues(issue_key, created_after_date)

    # Create the output directory if it doesn't exist
    output_directory = CONFIG['output_directory']
    os.makedirs(output_directory, exist_ok=True)

    if linked_issues:
        # Define output file paths
        output_filename = f"{output_directory}/linked_issues_{issue_key}.txt"
        custom_field_output_filename = f"{output_directory}/Resources_List_{issue_key}.json"

        # Initialize dictionaries to store custom field data
        main_custom_field_data = []
        custom_field_data_dict = {}

        # Get custom field data for the main issue
        main_issue_data = get_issue_data(issue_key)
        main_custom_field_data = main_issue_data.get('fields', {}).get('customfield_10330', [])
        if main_custom_field_data:
            custom_field_data_dict[issue_key] = main_custom_field_data

        # Get custom field data for linked issues
        for linked_issue, depth in linked_issues:
            linked_issue_data = get_issue_data(linked_issue)
            if linked_issue_data:
                custom_field_data = linked_issue_data.get('fields', {}).get('customfield_10330', [])
                if custom_field_data:
                    custom_field_data_dict[linked_issue] = custom_field_data

        # Write linked issues and custom field data to output files
        with open(output_filename, 'w') as output_file:
            output_file.write(f"Linked issues for {issue_key}:\n")
            for linked_issue, depth in linked_issues:
                output_file.write("  " * depth + linked_issue + '\n')
                print("  " * depth + linked_issue)

        with open(custom_field_output_filename, 'w') as custom_field_output_file:
            json.dump(custom_field_data_dict, custom_field_output_file, indent=2)

        print(f"Linked issues saved to {output_filename}")
        print(f"Custom field data saved to {custom_field_output_filename}")
    else:
        print(f"No linked issues found for {issue_key}")