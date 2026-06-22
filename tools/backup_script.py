import os, zipfile
from datetime import datetime

backup_name = f"SARACAPP_yedek_4.1.12_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
backup_path = os.path.join("C:\\Users\\bilal\\SARACAPP\\tools", backup_name)

exclude_dirs = {'.gradle', 'build', '.idea', '__pycache__', '0-versions', '.git'}

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            file_path = os.path.join(root, file)
            # Skip the backup file itself if it's being created inside the same tree
            if file_path == backup_path:
                continue
            arcname = os.path.relpath(file_path, path)
            ziph.write(file_path, arcname)

with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipdir("C:\\Users\\bilal\\SARACAPP", zipf)

print(f"Backup created at: {backup_path}")
