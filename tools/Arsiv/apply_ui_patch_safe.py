import codecs

filepath = 'C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

# 1. Spacers
text = text.replace('Spacer(modifier = Modifier.height(24.dp))', 'Spacer(modifier = Modifier.height(12.dp))')
text = text.replace('Spacer(modifier = Modifier.height(20.dp))', 'Spacer(modifier = Modifier.height(8.dp))')
text = text.replace('Spacer(modifier = Modifier.height(32.dp))', 'Spacer(modifier = Modifier.height(16.dp))')
text = text.replace('Modifier.padding(horizontal = 20.dp, vertical = 8.dp)', 'Modifier.padding(horizontal = 16.dp, vertical = 4.dp)')

# 2. Font sizes
text = text.replace('fontSize = 18.sp', 'fontSize = 15.sp')
text = text.replace('fontSize = 16.sp', 'fontSize = 13.sp')

# 3. İçerik Çıkar block
old_icerik = '''                Text("İçerik Çıkar", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary, fontSize = 15.sp)
                FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(top = 8.dp)) {
                    malzemeler_listesi.forEach { malz -> FilterChip(selected = seciliNotlar[malz] == true, onClick = { seciliNotlar[malz] = !(seciliNotlar[malz] ?: false) }, label = { Text(" Yok", fontSize = 13.sp, modifier = Modifier.padding(4.dp)) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFFE53935), selectedLabelColor = Color.White)) }
                }'''

new_icerik = '''                Text("İçerik", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary, fontSize = 15.sp)
                FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.padding(top = 4.dp)) {
                    val cikar = listOf("Soğan Yok", "Domates Yok", "Patates Yok", "Ketçap Yok", "Mayonez Yok", "Turşu Yok")
                    val ekle = listOf("Soğanlı", "Domatesli", "Patatesli", "Ketçaplı", "Mayonezli", "Turşulu")
                    cikar.forEach { malz -> FilterChip(selected = seciliNotlar[malz] == true, onClick = { seciliNotlar[malz] = !(seciliNotlar[malz] ?: false) }, label = { Text(malz, fontSize = 13.sp) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFFE53935), selectedLabelColor = Color.White)) }
                    ekle.forEach { malz -> FilterChip(selected = seciliNotlar[malz] == true, onClick = { seciliNotlar[malz] = !(seciliNotlar[malz] ?: false) }, label = { Text(malz, fontSize = 13.sp) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFF4CAF50), selectedLabelColor = Color.White)) }
                }'''
text = text.replace(old_icerik, new_icerik)

# 4. Fix tumNotlar generation
old_tumnotlar = 'tumNotlar.addAll(seciliNotlar.filter { it.value }.map { " yok" })'
new_tumnotlar = 'tumNotlar.addAll(seciliNotlar.filter { it.value }.map { it.key })'
text = text.replace(old_tumnotlar, new_tumnotlar)

# 5. Odeme logic
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

# 6. Icecek size and padding
text = text.replace('size(105.dp, 80.dp)', 'size(85.dp, 55.dp)')
text = text.replace('Text(ic.ad, color = Color.White, fontSize = 13.sp, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center, modifier = Modifier.padding(8.dp))', 'Text(ic.ad, color = Color.White, fontSize = 13.sp, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center, modifier = Modifier.padding(4.dp))')

# Update ucretli_ekstralar size
text = text.replace('Text(" (+₺)", fontSize = 15.sp, modifier = Modifier.padding(6.dp))', 'Text(" (+₺)", fontSize = 13.sp)')

with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(text)
print("Patch applied carefully.")
