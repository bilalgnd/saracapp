import codecs
import re

filepath = 'C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

# Fix Gramaj string interpolation using Regex
pattern = r'Text\(if\(sec\.gramaj == "Standart"\).*?\, fontSize = 13\.sp, fontWeight = FontWeight\.Bold\)'
replacement = r'Text(if(sec.gramaj == "Standart") "\ ₺" else "\ (\₺)", fontSize = 13.sp, fontWeight = FontWeight.Bold)'
if re.search(pattern, text):
    text = re.sub(pattern, replacement, text)
    print("Replaced Gramaj.")
else:
    print("Could not find Gramaj.")

with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(text)
