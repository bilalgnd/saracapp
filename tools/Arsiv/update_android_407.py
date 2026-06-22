import os
import codecs

# saracapp.kt
filepath = 'C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

# Version bump
text = text.replace('4.0.6', '4.0.7')

# Replace exact strings for cikar/zityon
# zityon = mapOf("Sogan Yok" to "Soganli" -> "Sogansiz" to "Soganli" etc...
old_zityon = 'val zityon = mapOf("Sogan Yok" to "Soganli", "Soganli" to "Sogan Yok", "Domates Yok" to "Domatesli", "Domatesli" to "Domates Yok", "Patates Yok" to "Patatesli", "Patatesli" to "Patates Yok", "Ketcap Yok" to "Ketcapli", "Ketcapli" to "Ketcap Yok", "Mayonez Yok" to "Mayonezli", "Mayonezli" to "Mayonez Yok", "Tursu Yok" to "Tursulu", "Tursulu" to "Tursu Yok")'
new_zityon = 'val zityon = mapOf("Sogansiz" to "Soganli", "Soganli" to "Sogansiz", "Domatessiz" to "Domatesli", "Domatesli" to "Domatessiz", "Patatessiz" to "Patatesli", "Patatesli" to "Patatessiz", "Ketcapsiz" to "Ketcapli", "Ketcapli" to "Ketcapsiz", "Mayonezsiz" to "Mayonezli", "Mayonezli" to "Mayonezsiz", "Tursusuz" to "Tursulu", "Tursulu" to "Tursusuz")'

old_cikar = 'val cikar = listOf("Sogan Yok", "Domates Yok", "Patates Yok", "Ketcap Yok", "Mayonez Yok", "Tursu Yok")'
new_cikar = 'val cikar = listOf("Sogansiz", "Domatessiz", "Patatessiz", "Ketcapsiz", "Mayonezsiz", "Tursusuz")'

old_basket = 'tumNotlar.addAll(seciliNotlar.filter { it.value }.map { "${it.key} yok" })'
new_basket = 'tumNotlar.addAll(seciliNotlar.filter { it.value }.map { it.key })'

text = text.replace(old_zityon, new_zityon)
text = text.replace(old_cikar, new_cikar)
text = text.replace(old_basket, new_basket)

with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(text)

# build.gradle.kts
gradle = 'C:/Users/bilal/AndroidStudioProjects/saracapp/app/build.gradle.kts'
with codecs.open(gradle, 'r', 'utf-8') as f:
    t2 = f.read()
t2 = t2.replace('versionCode = 4006', 'versionCode = 4007')
t2 = t2.replace('versionName = "4.0.6"', 'versionName = "4.0.7"')
with codecs.open(gradle, 'w', 'utf-8') as f:
    f.write(t2)

print("Updated Android code")
