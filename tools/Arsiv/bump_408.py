import os
import codecs
import re

app_js = 'C:/Users/bilal/SARACAPP/static/app.js'
with codecs.open(app_js, 'r', 'utf-8') as f:
    text = f.read()

# Fix Card Colors match strings
old_color_func = '''function getCardColorClass(name) {
    name = name.toLowerCase();
    if (name.includes("et porsiyon") || name.includes("pilav üstü beyti") || name.includes("iskender")) return "dark-red";
    if (name.includes("tavuk hatay usulü")) return "cream";
    if (name.includes("biga döner")) return "blue";
    if (name.includes("tavuk porsiyon") || name.includes("pilav üstü")) return "dark-orange";
    if (name.includes("tombik")) return "orange";
    if (name.includes("eski usul")) return "red";
    if (name.includes("dürüm")) return "yellow";
    return "";
}'''

new_color_func = '''function getCardColorClass(name) {
    name = name.toLowerCase();
    if (name.includes("et porsiyon") || name.includes("beyti") || name.includes("iskender")) return "dark-red";
    if (name.includes("hatay usulu")) return "cream";
    if (name.includes("biga doner")) return "blue";
    if (name.includes("tavuk porsiyon") || name.includes("pilav ustu")) return "dark-orange";
    if (name.includes("tombik")) return "orange";
    if (name.includes("eski usul")) return "red";
    if (name.includes("durum")) return "yellow";
    return "";
}'''

text = text.replace(old_color_func, new_color_func)
with codecs.open(app_js, 'w', 'utf-8') as f:
    f.write(text)

# BUMP VERSION TO 4.0.8
def bump(filepath, old_str, new_str):
    with codecs.open(filepath, 'r', 'utf-8') as f:
        t = f.read()
    t = t.replace(old_str, new_str)
    with codecs.open(filepath, 'w', 'utf-8') as f:
        f.write(t)

bump('C:/Users/bilal/SARACAPP/kasa_app.pyw', '4.0.7', '4.0.8')
bump('C:/Users/bilal/SARACAPP/templates/index.html', '4.0.7', '4.0.8')
bump('C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt', '4.0.7', '4.0.8')
bump('C:/Users/bilal/AndroidStudioProjects/saracapp/app/build.gradle.kts', 'versionName = "4.0.7"', 'versionName = "4.0.8"')
bump('C:/Users/bilal/AndroidStudioProjects/saracapp/app/build.gradle.kts', 'versionCode = 4007', 'versionCode = 4008')

print("Updated app.js logic and bumped version to 4.0.8")
