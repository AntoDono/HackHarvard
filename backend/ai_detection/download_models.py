from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

# Authenticate and create the PyDrive client.
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# Specify the folder ID (the part after 'folders/' in the URL)
folder_id = '1UmMTuXPmu-eYfskbrGgZ1uNXceznPQ6o'

# Create 'models' directory if it doesn't exist
if not os.path.exists('models'):
    os.makedirs('models')

# List all files in the folder
file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()

# Download each file to the 'models' directory
for file in file_list:
    file.GetContentFile(os.path.join('models', file['title']))

print("Download complete.")