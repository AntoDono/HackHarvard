"""
Download deepfake detection models from Google Drive.

This script downloads the required model files from a shared Google Drive folder.
Uses gdown for simplified downloading without OAuth authentication.
"""
import os
import subprocess

# Google Drive folder IDs and their names
folders = [
    {"id": "1iZEx8sQ_8i3EmHDvVwflbliMblMqtlIU", "name": "cnndetection_image"},
    {"id": "1iaLxJ79ytq82m-UjZQrBnJtpJOBo2_Q5", "name": "cvit_video"},
    {"id": "1BBYveJuuLjHKWip7eBoLBJ9M9Iu4N3dT", "name": "deepware_video"},
    {"id": "196kGVgg1kHmjcD1n8ESOeZbcORFn8tCI", "name": "faceforensics_video"},
    {"id": "1EbhIa3GwCMdE2ypvy8VUqCZpb3bU-O-U", "name": "ganimagedetection_video"},
    {"id": "11OHcVmU75LKRjgBQvOcwdOEY02GAwpx_", "name": "photoshop_fal_video"},
    {"id": "1-KYtH9v1YtsOLVsAjl4LCsU7LzjjVUpC", "name": "selim_video"},
]

# Create 'models' directory if it doesn't exist
if not os.path.exists('models'):
    os.makedirs('models')
    print("Created 'models' directory\n")

print("=" * 60)
print("Downloading deepfake detection models from Google Drive")
print("=" * 60)
print(f"Total models to download: {len(folders)}")
print("This may take a while depending on the size of the models...\n")

# Check if gdown is available
try:
    subprocess.run(['gdown', '--version'], capture_output=True, check=True)
except FileNotFoundError:
    print("✗ gdown not found. Please install it first:")
    print("   pip install gdown")
    exit(1)

# Download each model folder
successful = 0
failed = []

for idx, folder in enumerate(folders, 1):
    folder_id = folder['id']
    folder_name = folder['name']
    output_path = os.path.join('models', folder_name)
    
    print(f"[{idx}/{len(folders)}] Downloading {folder_name}...")
    
    try:
        # Download the folder contents and show progress in real time
        process = subprocess.Popen([
            'gdown',
            '--folder',
            f'https://drive.google.com/drive/folders/{folder_id}',
            '-O', output_path,
            '--remaining-ok'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Print output line by line to show progress
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print("    " + output.strip())
        # Capture any remaining output
        stdout, stderr = process.communicate()
        result = subprocess.CompletedProcess(
            process.args, process.returncode, stdout=stdout, stderr=stderr
        )
        
        if result.returncode == 0:
            print(f"  ✓ {folder_name} downloaded successfully\n")
            successful += 1
        else:
            print(f"  ✗ Failed to download {folder_name}")
            print(f"  Error: {result.stderr}\n")
            failed.append(folder_name)
    except Exception as e:
        print(f"  ✗ Error downloading {folder_name}: {e}\n")
        failed.append(folder_name)

# Summary
print("=" * 60)
print("Download Summary")
print("=" * 60)
print(f"✓ Successful: {successful}/{len(folders)}")
if failed:
    print(f"✗ Failed: {len(failed)}")
    for name in failed:
        print(f"  - {name}")
else:
    print("All models downloaded successfully!")
print("\nModels are ready in the 'models' directory.")