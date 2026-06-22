import os
import re
import codecs

def update_file(path, old, new):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
    try:
        with codecs.open(path, 'r', 'utf-8') as f:
            content = f.read()
        if old in content:
            content = content.replace(old, new)
            with codecs.open(path, 'w', 'utf-8') as f:
                f.write(content)
            print(f"Updated {path}")
    except Exception as e:
        print(f"Failed to update {path}: {e}")

# kasa_app.pyw
update_file('C:/Users/bilal/SARACAPP/kasa_app.pyw', '4.0.5', '4.0.6')

# index.html
update_file('C:/Users/bilal/SARACAPP/templates/index.html', '4.0.5', '4.0.6')

# Android build.gradle.kts
gradle_path = 'C:/Users/bilal/AndroidStudioProjects/saracapp/app/build.gradle.kts'
if os.path.exists(gradle_path):
    with codecs.open(gradle_path, 'r', 'utf-8') as f:
        content = f.read()
    content = content.replace('versionCode = 4005', 'versionCode = 4006')
    content = content.replace('versionName = "4.0.5"', 'versionName = "4.0.6"')
    with codecs.open(gradle_path, 'w', 'utf-8') as f:
        f.write(content)
    print(f"Updated {gradle_path}")

# saracapp.kt (credits/version)
update_file('C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt', '4.0.5', '4.0.6')

