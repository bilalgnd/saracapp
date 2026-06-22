import codecs
import re

filepath = 'C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

new_icerik = '''                Text("İçerik", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary, fontSize = 15.sp)
                FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.padding(top = 4.dp)) {
                    val cikar = listOf("Soğan Yok", "Domates Yok", "Patates Yok", "Ketçap Yok", "Mayonez Yok", "Turşu Yok")
                    val ekle = listOf("Soğanlı", "Domatesli", "Patatesli", "Ketçaplı", "Mayonezli", "Turşulu")
                    cikar.forEach { malz -> FilterChip(selected = seciliNotlar[malz] == true, onClick = { seciliNotlar[malz] = !(seciliNotlar[malz] ?: false) }, label = { Text(malz, fontSize = 13.sp) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFFE53935), selectedLabelColor = Color.White)) }
                    ekle.forEach { malz -> FilterChip(selected = seciliNotlar[malz] == true, onClick = { seciliNotlar[malz] = !(seciliNotlar[malz] ?: false) }, label = { Text(malz, fontSize = 13.sp) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFF4CAF50), selectedLabelColor = Color.White)) }
                }'''

pattern = r'Text\("İçerik Çıkar", fontWeight = FontWeight\.Bold, color = MaterialTheme\.colorScheme\.primary, fontSize = 15\.sp\)\s+FlowRow\(horizontalArrangement = Arrangement\.spacedBy\(8\.dp\), modifier = Modifier\.padding\(top = 8\.dp\)\) \{\s+malzemeler_listesi\.forEach \{ malz -> FilterChip.*?\}\s+\}'

if re.search(pattern, text, re.DOTALL):
    text = re.sub(pattern, new_icerik, text, flags=re.DOTALL)
    with codecs.open(filepath, 'w', 'utf-8') as f:
        f.write(text)
    print("İçerik block replaced via regex successfully.")
else:
    print("Could not match the regex pattern.")
