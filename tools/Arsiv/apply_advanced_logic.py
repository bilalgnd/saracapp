import codecs
import re

filepath = 'C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

# 1. Product Colors Update
old_urun_karti_when = '''    val bgRenk = when {
        urun.ad.contains("Tombik", ignoreCase = true) -> Color(0xFFFF9800)
        urun.ad.contains("Eski Usul", ignoreCase = true) -> Color(0xFFF44336)
        urun.ad.contains("Dürüm", ignoreCase = true) -> Color(0xFFFFEB3B)
        else -> Color(0xFF242424)
    }
    val yaziRengi = if (bgRenk == Color(0xFFFFEB3B) || bgRenk == Color(0xFFFF9800)) Color.Black else Color.White
    val fiyatRengi = if (bgRenk == Color(0xFF242424)) MaterialTheme.colorScheme.primary else if (bgRenk == Color(0xFFFFEB3B) || bgRenk == Color(0xFFFF9800)) Color(0xFF333333) else Color.White'''

new_urun_karti_when = '''    val adLc = urun.ad.lowercase()
    val bgRenk = when {
        adLc.contains("tombik") -> Color(0xFFFF9800)
        adLc.contains("eski usul") -> Color(0xFFF44336)
        adLc.contains("dürüm") -> Color(0xFFFFEB3B)
        adLc.contains("et porsiyon") || adLc.contains("beyti") || adLc.contains("iskender") || (adLc.contains("pilav üstü") && !adLc.contains("tavuk")) -> Color(0xFF8B0000)
        adLc.contains("tavuk hatay") -> Color(0xFFF5DEB3)
        adLc.contains("biga") -> Color(0xFF1976D2)
        adLc.contains("tavuk porsiyon") || (adLc.contains("pilav üstü") && adLc.contains("tavuk")) -> Color(0xFFFF5722)
        else -> Color(0xFF242424)
    }
    val isLightBg = bgRenk == Color(0xFFFFEB3B) || bgRenk == Color(0xFFFF9800) || bgRenk == Color(0xFFF5DEB3) || bgRenk == Color(0xFFFF5722)
    val yaziRengi = if (isLightBg) Color.Black else Color.White
    val fiyatRengi = if (bgRenk == Color(0xFF242424)) MaterialTheme.colorScheme.primary else if (isLightBg) Color(0xFF333333) else Color.White'''

if old_urun_karti_when in text:
    text = text.replace(old_urun_karti_when, new_urun_karti_when)
    print("Product colors updated.")

# 2. Mutually exclusive ingredients and Cheddar/Kaşarlı move
# Find the İçerik block
icerik_pattern = r'val cikar = listOf\("Soğan Yok",.*?val ekle = listOf\("Soğanlı",.*?"Turşulu"\)'
if re.search(icerik_pattern, text, re.DOTALL):
    icerik_replacement = '''val zityon = mapOf("Soğan Yok" to "Soğanlı", "Soğanlı" to "Soğan Yok", "Domates Yok" to "Domatesli", "Domatesli" to "Domates Yok", "Patates Yok" to "Patatesli", "Patatesli" to "Patates Yok", "Ketçap Yok" to "Ketçaplı", "Ketçaplı" to "Ketçap Yok", "Mayonez Yok" to "Mayonezli", "Mayonezli" to "Mayonez Yok", "Turşu Yok" to "Turşulu", "Turşulu" to "Turşu Yok")
                    val cikar = listOf("Soğan Yok", "Domates Yok", "Patates Yok", "Ketçap Yok", "Mayonez Yok", "Turşu Yok")
                    val ekle = listOf("Soğanlı", "Domatesli", "Patatesli", "Ketçaplı", "Mayonezli", "Turşulu")'''
    text = re.sub(icerik_pattern, icerik_replacement, text, flags=re.DOTALL)
    print("Icerik maps added.")

old_cikar_click = 'onClick = { seciliNotlar[malz] = !(seciliNotlar[malz] ?: false) }'
new_cikar_click = 'onClick = { val s = !(seciliNotlar[malz] ?: false); seciliNotlar[malz] = s; if(s && zityon.containsKey(malz)) seciliNotlar[zityon[malz]!!] = false }'
text = text.replace(old_cikar_click, new_cikar_click)

# Add Cheddar and Kaşarlı loops to İçerik FlowRow
old_ekle_foreach = 'ekle.forEach { malz -> FilterChip(selected = seciliNotlar[malz] == true, onClick = { val s = !(seciliNotlar[malz] ?: false); seciliNotlar[malz] = s; if(s && zityon.containsKey(malz)) seciliNotlar[zityon[malz]!!] = false }, label = { Text(malz, fontSize = 13.sp) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFF4CAF50), selectedLabelColor = Color.White)) }'
new_ekle_foreach = old_ekle_foreach + '''
                    listOf("Cheddar", "Kaşarlı").forEach { malz -> if(ucretliEkstralar.containsKey(malz)) { FilterChip(selected = seciliUcretliEkstralar[malz] == true, onClick = { seciliUcretliEkstralar[malz] = !(seciliUcretliEkstralar[malz] ?: false) }, label = { Text(malz, fontSize = 13.sp) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFFFFD54F), selectedLabelColor = Color.Black)) } }'''
if old_ekle_foreach in text:
    text = text.replace(old_ekle_foreach, new_ekle_foreach)
    print("Added Cheddar to Icerik.")
else:
    print("Could not find ekle_foreach")

# Hide Cheddar and Kaşarlı from Ucretli Ekstralar section
old_ucretli_block = '''                Text("Ücretli Ekstralar", fontWeight = FontWeight.Bold, color = Color(0xFFFFD54F), fontSize = 15.sp)
                FlowRow(horizontalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.padding(top = 8.dp)) {
                    ucretliEkstralar.forEach { (isim, fiyat) -> FilterChip(selected = seciliUcretliEkstralar[isim] == true, onClick = { seciliUcretliEkstralar[isim] = !(seciliUcretliEkstralar[isim] ?: false) }, label = { Text(" (+₺)", fontSize = 15.sp, modifier = Modifier.padding(6.dp)) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFFFFD54F), selectedLabelColor = Color.Black)) }
                }
                Spacer(modifier = Modifier.height(8.dp))'''

new_ucretli_block = '''                val digerUcretliler = ucretliEkstralar.filterKeys { it != "Cheddar" && it != "Kaşarlı" }
                if (digerUcretliler.isNotEmpty()) {
                    Text("Ücretli Ekstralar", fontWeight = FontWeight.Bold, color = Color(0xFFFFD54F), fontSize = 15.sp)
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.padding(top = 8.dp)) {
                        digerUcretliler.forEach { (isim, fiyat) -> FilterChip(selected = seciliUcretliEkstralar[isim] == true, onClick = { seciliUcretliEkstralar[isim] = !(seciliUcretliEkstralar[isim] ?: false) }, label = { Text(" (+₺)", fontSize = 13.sp, fontWeight = FontWeight.Bold) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFFFFD54F), selectedLabelColor = Color.Black)) }
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                }'''
text = text.replace(old_ucretli_block, new_ucretli_block)

# 3. Icecek Colors
old_icecek_box = '.background(if (miktar > 0) Color(0xFF388E3C) else Color(0xFF242424), RoundedCornerShape(12.dp))'
new_icecek_box = '''.background(
                                        color = when {
                                            ic.ad.lowercase().contains("kutu kola") || ic.ad.lowercase().contains("şişe kola") -> Color(0xFFF40009)
                                            ic.ad.lowercase().contains("sprite") -> Color(0xFF008B47)
                                            ic.ad.lowercase().contains("fanta") -> Color(0xFFF58216)
                                            ic.ad.lowercase().contains("ayran") -> Color(0xFFFDFD96)
                                            ic.ad.lowercase().contains("su") && !ic.ad.lowercase().contains("usul") -> Color(0xFF00BFFF)
                                            ic.ad.lowercase().contains("soda") -> Color(0xFF006400)
                                            ic.ad.lowercase().contains("şalgam") -> Color(0xFF800080)
                                            ic.ad.lowercase().contains("zero") -> Color(0xFF111111)
                                            else -> Color(0xFF242424)
                                        }.let { if (miktar > 0) it else it.copy(alpha = 0.4f) },
                                        shape = RoundedCornerShape(12.dp)
                                    )'''
text = text.replace(old_icecek_box, new_icecek_box)

# 4. Icecek text color depending on background
old_icecek_text = 'Text(ic.ad, color = Color.White, fontSize = 11.sp, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center, modifier = Modifier.padding(2.dp), lineHeight = 12.sp)'
new_icecek_text = 'val yRengi = if (ic.ad.lowercase().contains("ayran")) Color.Black else Color.White\n                                Text(ic.ad, color = yRengi, fontSize = 11.sp, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center, modifier = Modifier.padding(2.dp), lineHeight = 12.sp)'
text = text.replace(old_icecek_text, new_icecek_text)

with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(text)
print("Saracapp.kt fully updated.")
