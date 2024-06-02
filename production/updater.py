import time
import requests
import subprocess  # For secure updates using Git
from datetime import datetime, timedelta  # For scheduling daily checks
import os
import shutil
import stat  # Import the stat module
import platform

# Replace with your actual GitHub repository URL
repo_url = "https://api.github.com/sc4321/rCare/upload/main/production"
repo_cloning_url = "https://github.com/sc4321/rCare/upload/main/production.git"

# Last update file path
last_update_file = "last_updated_time.txt"
CLONED_FOLDER_PATH = "./updated_project"
# Update check interval (in days)
update_interval = 1

# Magic numbers:
REQUEST_HAS_SUCCEEDED = 200
RETRIES_FOR_INTERNET_FAILURE = 5
RETRIES_FOR_CLONING_FAILURE = 5


def get_last_update_time():
    if not os.path.exists(last_update_file):
        # Create the last update file (without writing anything initially)
        with open(last_update_file, "w") as f:
            f.write(str(datetime.now()))
        return None

    try:
        # Read last update time from file
        with open(last_update_file, "r") as f:
            last_update_str = f.readline().strip()
            return datetime.strptime(last_update_str, "%Y-%m-%d %H:%M:%S.%f")  # Parse with millisecond precision
    except (FileNotFoundError, ValueError):
        # Handle errors: create empty file or invalid format
        print(f"Error reading last update file. Creating new file.")
        with open(last_update_file, "w") as f:
            f.write(str(datetime.now()))
        return None


def check_for_update():
    last_update_time = get_last_update_time()
    if last_update_time is None:
        return  # Handle error getting last update time

    # Check if the last update was more than a day ago
    # if datetime.now() - last_update_time < timedelta(days=update_interval): # todo
    if datetime.now() - last_update_time < timedelta(seconds=update_interval):
        print("Last update was within the last day. Skipping update check.")
        return

    max_retries = RETRIES_FOR_INTERNET_FAILURE  # Set the maximum number of retries for request.get
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(repo_url + "/releases/latest")
            if response.status_code == REQUEST_HAS_SUCCEEDED:
                latest_version_tag_name = response.json()["tag_name"]

                # Read current version from version.txt
                try:
                    with open("version.txt", "r") as f:
                        current_version = float(f.readline().strip())
                except FileNotFoundError:
                    # No version file, assume no previous version
                    current_version = 0.0

                # Compare versions (assuming version.txt stores a float)
                if float(latest_version_tag_name) > current_version:
                    update_script(latest_version_tag_name)
                else:
                    print(f"Already on latest version: {current_version}")
                break  # Exit loop on successful request
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt}/{max_retries}: Error fetching update info: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff between retries
    else:
        print("Failed to retrieve update information after retries.")


def update_script(latest_version):
    max_retries = RETRIES_FOR_CLONING_FAILURE  # Set the maximum number of retries for cloning
    for attempt in range(1, max_retries + 1):
        try:
            delete_folder_safely(CLONED_FOLDER_PATH)
            subprocess.run(["git", "clone", "--depth=1", repo_cloning_url, CLONED_FOLDER_PATH], check=True)

            # Replace existing files with updated versions
            shutil.copy2(os.path.join(CLONED_FOLDER_PATH, "the_functionality.py"), ".")
            # shutil.copy2(os.path.join(CLONED_FOLDER_PATH, "updater.py"), ".")  # todo uncomment after updating github

            # Update version file with latest version
            with open("version.txt", "w") as f:
                f.write(latest_version)

            # Update last update time after successful execution
            with open(last_update_file, "w") as f:
                f.write(str(datetime.now()))

            print("Successfully updated project from GitHub!")
            delete_folder_safely(CLONED_FOLDER_PATH)
            break  # Exit loop on successful cloning
        except subprocess.CalledProcessError as e:
            print(f"Attempt {attempt}/{max_retries}: Error cloning repository: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff between retries
    else:
        print("Failed to clone the updated project after retries.")


def delete_folder_safely(folder_path):
    if not os.path.exists(folder_path):
        return  # no folder preventing cloning success
    try:
        shutil.rmtree(folder_path, ignore_errors=False)
    except PermissionError as e:
        print(f"Permission error encountered: {e}")
        if platform.system() == "Windows":
            change_permissions_recursive_windows(folder_path)  # Change permissions to writable for Windows
        else:
            change_permissions_recursive(folder_path, stat.S_IWRITE)  # Change permissions to writable for Unix
        shutil.rmtree(folder_path, ignore_errors=False)  # Retry deletion
    except OSError as e:
        raise OSError(f"Error deleting folder: {folder_path}") from e
    print(f"Successfully deleted folder: {folder_path}")


def change_permissions_recursive(path, mode):
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            os.chmod(os.path.join(root, dir), mode)
        for file in files:
            os.chmod(os.path.join(root, file), mode)


def change_permissions_recursive_windows(path):
    import ctypes
    file_attribute_readonly = 0x01

    def unset_readonly(file):
        attrs = ctypes.windll.kernel32.GetFileAttributesW(file)
        if attrs & file_attribute_readonly:
            ctypes.windll.kernel32.SetFileAttributesW(file, attrs & ~file_attribute_readonly)

    for root, dirs, files in os.walk(path):
        for dir in dirs:
            unset_readonly(os.path.join(root, dir))
        for file in files:
            unset_readonly(os.path.join(root, file))


if __name__ == "__main__":
    check_for_update()
