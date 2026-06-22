import os
import codecs

def bump(filepath, old_str, new_str):
    with codecs.open(filepath, 'r', 'utf-8') as f:
        t = f.read()
    t = t.replace(old_str, new_str)
    with codecs.open(filepath, 'w', 'utf-8') as f:
        f.write(t)

bump('C:/Users/bilal/SARACAPP/kasa_app.pyw', '4.0.8', '4.0.9')
bump('C:/Users/bilal/SARACAPP/templates/index.html', '4.0.8', '4.0.9')
bump('C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt', '4.0.8', '4.0.9')
bump('C:/Users/bilal/AndroidStudioProjects/saracapp/app/build.gradle.kts', 'versionName = "4.0.8"', 'versionName = "4.0.9"')
bump('C:/Users/bilal/AndroidStudioProjects/saracapp/app/build.gradle.kts', 'versionCode = 4008', 'versionCode = 4009')

print("Bumped version to 4.0.9")
