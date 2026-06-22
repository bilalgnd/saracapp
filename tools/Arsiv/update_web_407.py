import os
import codecs

# index.html
filepath = 'C:/Users/bilal/SARACAPP/templates/index.html'
if os.path.exists(filepath):
    with codecs.open(filepath, 'r', 'utf-8') as f:
        text = f.read()
    text = text.replace('4.0.6', '4.0.7')
    with codecs.open(filepath, 'w', 'utf-8') as f:
        f.write(text)
    print("Updated index.html to 4.0.7")
