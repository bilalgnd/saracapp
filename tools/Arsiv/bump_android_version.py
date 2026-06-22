import codecs
import re

# Update build.gradle.kts
filepath_gradle = 'C:/Users/bilal/AndroidStudioProjects/saracapp/app/build.gradle.kts'
with codecs.open(filepath_gradle, 'r', 'utf-8') as f:
    text_gradle = f.read()

text_gradle = re.sub(r'versionCode = \d+', 'versionCode = 4005', text_gradle)
text_gradle = re.sub(r'versionName = ".*?"', 'versionName = "4.0.5"', text_gradle)

with codecs.open(filepath_gradle, 'w', 'utf-8') as f:
    f.write(text_gradle)

print("Updated build.gradle.kts")
