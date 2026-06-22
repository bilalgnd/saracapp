import os
import codecs
import re
import sys

def bump(filepath, old_str, new_str, regex=False):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    with codecs.open(filepath, 'r', 'utf-8') as f:
        t = f.read()
    if regex:
        t = re.sub(old_str, new_str, t)
    else:
        t = t.replace(old_str, new_str)
    with codecs.open(filepath, 'w', 'utf-8') as f:
        f.write(t)
    print(f"Updated {filepath}")

def main(old_ver, new_ver):
    # Parse versions
    # old_ver = "4.1.0", new_ver = "4.1.1"
    old_vc = old_ver.replace('.', '0') # e.g. 4010
    new_vc = new_ver.replace('.', '0')

    # Update Python UI
    bump('C:/Users/bilal/SARACAPP/saracapp_ui.py', f'v{old_ver}', f'v{new_ver}')
    
    # Update HTML
    bump('C:/Users/bilal/SARACAPP/templates/index.html', f'v{old_ver}', f'v{new_ver}')
    
    # Update Kotlin app
    bump('C:/Users/bilal/SARACAPP/saracapp2/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt', old_ver, new_ver)
    
    # Update Gradle
    bump('C:/Users/bilal/SARACAPP/saracapp2/app/build.gradle.kts', f'versionName = "{old_ver}"', f'versionName = "{new_ver}"')
    bump('C:/Users/bilal/SARACAPP/saracapp2/app/build.gradle.kts', f'versionCode = {old_vc}', f'versionCode = {new_vc}')

    print(f"Successfully bumped version from {old_ver} to {new_ver} across all platforms.")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python bump_version.py <old_version> <new_version>")
        print("Example: python bump_version.py 4.1.0 4.1.1")
    else:
        main(sys.argv[1], sys.argv[2])
