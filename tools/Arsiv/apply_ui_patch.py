import codecs
import re

filepath = 'C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

# 1. Update Spacers to be more compact
text = text.replace('Spacer(modifier = Modifier.height(24.dp))', 'Spacer(modifier = Modifier.height(12.dp))')
text = text.replace('Spacer(modifier = Modifier.height(20.dp))', 'Spacer(modifier = Modifier.height(8.dp))')
text = text.replace('Spacer(modifier = Modifier.height(32.dp))', 'Spacer(modifier = Modifier.height(16.dp))')
text = text.replace('Modifier.padding(horizontal = 20.dp, vertical = 8.dp)', 'Modifier.padding(horizontal = 16.dp, vertical = 4.dp)')

# 2. Update section titles font size
text = text.replace('fontSize = 18.sp', 'fontSize = 15.sp')

# 3. Update ingredients section (İçerik Çıkar)
old_icerik = '''                Text("İçerik Çıkar", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary, fontSize = 15.sp)
                FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(top = 8.dp)) {
                    malzemeler_listesi.forEach { malz -> FilterChip(selected = seciliNotlar[malz] == true, onClick = { seciliNotlar[malz] = !(seciliNotlar[malz] ?: false) }, label = { Text(" Yok", fontSize = 16.sp, modifier = Modifier.padding(4.dp)) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFFE53935), selectedLabelColor = Color.White)) }
                }'''
new_icerik = '''                Text("İçerik", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary, fontSize = 15.sp)
                FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.padding(top = 4.dp)) {
                    val cikar = listOf("Soğan Yok", "Domates Yok", "Patates Yok", "Ketçap Yok", "Mayonez Yok", "Turşu Yok")
                    val ekle = listOf("Soğanlı", "Domatesli", "Patatesli", "Ketçaplı", "Mayonezli", "Turşulu")
                    cikar.forEach { malz -> FilterChip(selected = seciliNotlar[malz] == true, onClick = { seciliNotlar[malz] = !(seciliNotlar[malz] ?: false) }, label = { Text(malz, fontSize = 13.sp) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFFE53935), selectedLabelColor = Color.White)) }
                    ekle.forEach { malz -> FilterChip(selected = seciliNotlar[malz] == true, onClick = { seciliNotlar[malz] = !(seciliNotlar[malz] ?: false) }, label = { Text(malz, fontSize = 13.sp) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFF4CAF50), selectedLabelColor = Color.White)) }
                }'''
if 'Text("İçerik Çıkar", fontWeight = FontWeight.Bold' in text:
    # First revert the fontSize 18->15 replacement for this block just for matching if needed, but it's already 15.sp in old_icerik
    if old_icerik in text:
        text = text.replace(old_icerik, new_icerik)
    else:
        # try regex for flexibility
        text = re.sub(r'Text\("İçerik Çıkar".*?FlowRow.*?\n.*?\n.*?\n.*?\s+\}', new_icerik, text, flags=re.DOTALL)

# 4. Update ekstralar and notlar to be smaller
text = text.replace('Text(" (+₺)", fontSize = 15.sp, modifier = Modifier.padding(6.dp))', 'Text(" (+₺)", fontSize = 13.sp)')
text = text.replace('Text(eks, fontSize = 16.sp)', 'Text(eks, fontSize = 13.sp)')
text = text.replace('Text(odm, fontSize = 16.sp)', 'Text(odm, fontSize = 13.sp)')

# 5. Fix tumNotlar generation
old_tumnotlar = 'tumNotlar.addAll(seciliNotlar.filter { it.value }.map { " yok" })'
new_tumnotlar = 'tumNotlar.addAll(seciliNotlar.filter { it.value }.map { it.key })'
text = text.replace(old_tumnotlar, new_tumnotlar)

# 6. Update Odeme mutually exclusive logic
old_odeme = 'FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) { odeme_listesi.forEach { odm -> FilterChip(selected = seciliOdemeler[odm] == true, onClick = { seciliOdemeler[odm] = !(seciliOdemeler[odm] ?: false) }, label = { Text(odm, fontSize = 13.sp) }) } }'
new_odeme = '''FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp)) { odeme_listesi.forEach { odm -> FilterChip(selected = seciliOdemeler[odm] == true, onClick = { 
                            val newVal = !(seciliOdemeler[odm] ?: false)
                            seciliOdemeler[odm] = newVal
                            if (newVal) {
                                if (odm == "POS") seciliOdemeler["NAKİT"] = false
                                if (odm == "NAKİT") seciliOdemeler["POS"] = false
                                if (odm == "Paket") seciliOdemeler["Dükkan içi"] = false
                                if (odm == "Dükkan içi") seciliOdemeler["Paket"] = false
                            }
                        }, label = { Text(odm, fontSize = 13.sp) }) } }'''
text = text.replace(old_odeme, new_odeme)

# 7. Make Icecek container smaller
text = text.replace('size(105.dp, 80.dp)', 'size(85.dp, 55.dp)')
text = text.replace('Text(ic.ad, color = Color.White, fontSize = 16.sp, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center, modifier = Modifier.padding(8.dp))', 'Text(ic.ad, color = Color.White, fontSize = 14.sp, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center, modifier = Modifier.padding(4.dp))')

with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(text)
print("Patch applied successfully.")
