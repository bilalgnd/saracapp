import os
import shutil
import datetime

def take_daily_backup():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backups_dir = os.path.join(project_root, "tools", "backups")
    os.makedirs(backups_dir, exist_ok=True)
    
    today = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_name = f"saracapp_backup_{today}"
    backup_path = os.path.join(backups_dir, backup_name)
    
    print(f"Starting backup: {backup_name}...")
    
    try:
        # Ignore backups folder itself to prevent recursive inflation
        def ignore_func(dir, contents):
            if os.path.basename(dir) == 'backups' or os.path.basename(dir) == '0-versions':
                return contents
            return []
            
        shutil.make_archive(backup_path, 'zip', project_root)
        print(f"Backup successfully created at: {backup_path}.zip")
    except Exception as e:
        print(f"Error creating backup: {e}")

if __name__ == "__main__":
    take_daily_backup()
