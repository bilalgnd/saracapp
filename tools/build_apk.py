import os
import subprocess
import shutil

def get_version():
    ui_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saracapp_ui.py")
    if os.path.exists(ui_path):
        with open(ui_path, "r", encoding="utf-8") as f:
            for line in f:
                if "MEVCUT_VERSIYON" in line:
                    return line.split("=")[1].strip().replace('"', '').replace("'", "").replace("v", "")
    return "unknown"

def build_apk():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    android_dir = os.path.join(project_root, "saracapp2")
    output_dir = os.path.join(project_root, "0-versions")
    
    os.makedirs(output_dir, exist_ok=True)
    
    version = get_version()
    
    # Run gradle build
    print("Building Android APK...")
    result = subprocess.run(["gradlew.bat", "assembleDebug"], cwd=android_dir, shell=True)
    
    if result.returncode != 0:
        print("Error: Gradle build failed!")
        return
    
    # Copy APK
    source_apk = os.path.join(android_dir, "app", "build", "outputs", "apk", "debug", "app-debug.apk")
    target_apk = os.path.join(output_dir, f"saracapp{version}.apk")
    
    if os.path.exists(source_apk):
        shutil.copy2(source_apk, target_apk)
        print(f"Successfully built and copied to: {target_apk}")
    else:
        print(f"Error: APK not found at {source_apk}")

if __name__ == "__main__":
    build_apk()
