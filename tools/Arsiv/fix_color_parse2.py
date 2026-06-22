import codecs

filepath = 'C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

old_code = '''                    if (!adisyon.renk.isNullOrBlank()) {
                        try {
                            Box(modifier = Modifier.size(16.dp).background(Color(android.graphics.Color.parseColor(adisyon.renk)), CircleShape))
                            Spacer(modifier = Modifier.width(8.dp))
                        } catch (e: Exception) {}
                    }'''

new_code = '''                    if (!adisyon.renk.isNullOrBlank()) {
                        val pColor = try { android.graphics.Color.parseColor(adisyon.renk) } catch(e: Exception) { android.graphics.Color.TRANSPARENT }
                        if (pColor != android.graphics.Color.TRANSPARENT) {
                            Box(modifier = Modifier.size(16.dp).background(Color(pColor), CircleShape))
                            Spacer(modifier = Modifier.width(8.dp))
                        }
                    }'''

if old_code in text:
    text = text.replace(old_code, new_code)
    with codecs.open(filepath, 'w', 'utf-8') as f:
        f.write(text)
    print("Replaced successfully")
else:
    print("Old code not found")
