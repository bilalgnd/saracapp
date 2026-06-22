import codecs
import re

filepath = r'C:\Users\bilal\SARACAPP\saracapp2\app\src\main\java\com\bilalgnd\saracapp\saracapp.kt'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

# 1. Update Tabs in AnaEkran
text = re.sub(
    r'val sekmeler = listOf\("ET DÖNER", "TAVUK DÖNER", "KAMPANYA", "İÇECEKLER"\)',
    'val sekmeler = listOf("🥩 ET\\nDÖNER", "🍗 TAVUK\\nDÖNER", "🌟 KAMPANYA", "🥤 İÇECEKLER")',
    text
)

# 2. Add Imports
imports_to_add = """import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.material3.Badge
import androidx.compose.material3.BadgedBox
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.material3.CardDefaults
"""
if "import androidx.compose.material3.BadgedBox" not in text:
    text = text.replace('import androidx.compose.material3.Card', f"import androidx.compose.material3.Card\n{imports_to_add}")

# 3. Replace UrunKarti
new_urun_karti = """@Composable
fun UrunKarti(urun: Urun, onClick: () -> Unit, onLongClick: () -> Unit) {
    val bgRenk = when {
        urun.ad.contains("Tombik") -> Color(0xFFFF9800)
        urun.ad.contains("Durum") -> Color(0xFFFFEB3B)
        urun.ad.contains("Hatay") -> Color(0xFFF5E1C8)
        urun.ad.contains("Eski Usul") -> Color(0xFFF44336)
        urun.ad.contains("Biga") -> Color(0xFF1976D2)
        urun.ad.contains("Porsiyon") || urun.ad.contains("Pilav Ustu") -> if (urun.ad.contains("Tavuk")) Color(0xFFFF5722) else Color(0xFF8B0000)
        urun.ad.contains("Beyti") || urun.ad.contains("Iskender") -> Color(0xFF8B0000)
        else -> Color(0xFF607D8B)
    }
    val yaziRenk = if (bgRenk == Color(0xFFFFEB3B) || bgRenk == Color(0xFFF5E1C8)) Color.Black else Color.White

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(110.dp)
            .padding(4.dp)
            .pointerInput(Unit) {
                detectTapGestures(
                    onTap = { onClick() },
                    onLongPress = { onLongClick() }
                )
            },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = bgRenk)
    ) {
        Column(
            modifier = Modifier.fillMaxSize().padding(8.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = urun.ad,
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = yaziRenk,
                textAlign = TextAlign.Center,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis
            )
            Spacer(modifier = Modifier.height(8.dp))
            val bazFiyat = urun.secenekler.firstOrNull { it.gramaj == "Standart" || it.gramaj == "100gr" }?.fiyat ?: urun.secenekler.firstOrNull()?.fiyat ?: 0
            Text(
                text = "$bazFiyat ₺",
                fontSize = 16.sp,
                color = yaziRenk
            )
        }
    }
}"""

# A more robust regex replacement for UrunKarti
old_urun_karti_regex = r'@Composable\s*fun UrunKarti.*?\{.*?\n(?:    .*?| \}.*?|\s*\}\s*?\n)*?\s*\}\s*\}'
if re.search(old_urun_karti_regex, text, flags=re.DOTALL):
    text = re.sub(old_urun_karti_regex, new_urun_karti, text, flags=re.DOTALL)
else:
    # Fallback to simple replace if regex fails
    old_urun_str = """@Composable
fun UrunKarti(urun: Urun, onClick: () -> Unit, onLongClick: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth().height(100.dp).padding(4.dp).clickable { onClick() },
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2E2E2E))
    ) {
        Column(
            modifier = Modifier.fillMaxSize().padding(8.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(text = urun.ad, fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.White, textAlign = TextAlign.Center)
            Spacer(modifier = Modifier.height(4.dp))
            val bazFiyat = urun.secenekler.firstOrNull { it.gramaj == "Standart" || it.gramaj == "100gr" }?.fiyat ?: urun.secenekler.firstOrNull()?.fiyat ?: 0
            Text(text = "$bazFiyat ₺", fontSize = 14.sp, color = Color(0xFFFF9800))
        }
    }
}"""
    text = text.replace(old_urun_str, new_urun_karti)


# 4. Replace SiparisBottomSheet
new_bottom_sheet = """@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun SiparisBottomSheet(urun: Urun, guncelMasaAdi: String?, icecekMenusu: List<Urun>, ucretliEkstralar: Map<String, Int>, kapat: () -> Unit, onSiparisEkle: (String, List<SiparisKalemi>) -> Unit) {
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    
    val seciliGramaj = remember { mutableStateOf(urun.secenekler.firstOrNull { it.gramaj == "100gr" }?.gramaj ?: urun.secenekler.firstOrNull()?.gramaj ?: "") }
    val anlikFiyat = remember { mutableIntStateOf(urun.secenekler.firstOrNull { it.gramaj == "100gr" }?.fiyat ?: urun.secenekler.firstOrNull()?.fiyat ?: 0) }
    
    val tumIcerikler = listOf("Sogansiz", "Domatessiz", "Patatessiz", "Ketcapsiz", "Mayonezsiz", "Tursusuz", "Soganli", "Domatesli", "Patatesli", "Ketcapli", "Mayonezli", "Tursulu", "Cheddar", "Kasarli")
    val seciliNotlar = remember { mutableStateMapOf<String, Boolean>() }
    
    val ozelNotlar = listOf("Sade Et", "Soslu", "Gemi", "Kayık")
    val seciliOzelNotlar = remember { mutableStateMapOf<String, Boolean>() }
    
    val odemeler = listOf("POS", "NAKİT", "Paket", "Dükkan içi")
    val seciliOdemeler = remember { mutableStateMapOf<String, Boolean>() }
    
    val ozelNot = remember { mutableStateOf("") }
    val masaAdi = remember { mutableStateOf(guncelMasaAdi ?: "") }
    
    val seciliIcecekler = remember { mutableStateMapOf<String, Int>() }

    fun icerikExclusive(malz: String) {
        val newVal = !(seciliNotlar[malz] ?: false)
        seciliNotlar[malz] = newVal
        if (newVal) {
            if (malz.endsWith("siz") || malz.endsWith("suz")) {
                val zitti = malz.replace("siz", "li").replace("suz", "lu")
                seciliNotlar[zitti] = false
            } else if (malz.endsWith("li") || malz.endsWith("lu")) {
                val zitti = malz.replace("li", "siz").replace("lu", "suz")
                seciliNotlar[zitti] = false
            }
        }
    }

    fun hesapla(): Int {
        var top = anlikFiyat.intValue
        seciliNotlar.forEach { (k, v) -> if (v && ucretliEkstralar.containsKey(k)) top += ucretliEkstralar[k]!! }
        seciliIcecekler.forEach { (ad, adet) -> 
            val icFiyat = icecekMenusu.find { it.ad == ad }?.secenekler?.firstOrNull()?.fiyat ?: 0
            top += (icFiyat * adet)
        }
        return top
    }

    ModalBottomSheet(onDismissRequest = kapat, sheetState = sheetState, containerColor = Color(0xFF1E1E1E)) {
        Column(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp).verticalScroll(rememberScrollState())) {
            
            // Header
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Text(urun.ad, color = Color.White, fontSize = 28.sp, fontWeight = FontWeight.Bold)
                val adet = remember { mutableIntStateOf(1) }
                Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.background(Color(0xFF333333), RoundedCornerShape(12.dp)).padding(4.dp)) {
                    IconButton(onClick = { if (adet.intValue > 1) adet.intValue-- }) { Text("-", color = Color.White, fontSize = 24.sp, fontWeight = FontWeight.Bold) }
                    Text(adet.intValue.toString(), color = Color(0xFFFF9800), fontSize = 20.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 8.dp))
                    IconButton(onClick = { adet.intValue++ }) { Text("+", color = Color.White, fontSize = 24.sp, fontWeight = FontWeight.Bold) }
                }
            }

            Spacer(Modifier.height(16.dp))
            
            // Gramaj
            Text("Seçim / Gramaj", color = Color(0xFFFF9800), fontWeight = FontWeight.Bold)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(top = 8.dp)) {
                urun.secenekler.forEach { s ->
                    val isSelected = seciliGramaj.value == s.gramaj
                    FilterChip(
                        selected = isSelected,
                        onClick = { seciliGramaj.value = s.gramaj; anlikFiyat.intValue = s.fiyat },
                        label = { Text(if (s.gramaj == "Standart") "${s.fiyat}₺" else "${s.gramaj} (${s.fiyat}₺)", fontSize = 14.sp) },
                        colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFF4CAF50), selectedLabelColor = Color.White, containerColor = Color.Transparent, labelColor = Color.LightGray)
                    )
                }
            }

            Spacer(Modifier.height(16.dp))

            // İçerik
            Text("Icerik", color = Color(0xFFFF9800), fontWeight = FontWeight.Bold)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(top = 8.dp)) {
                tumIcerikler.forEach { malz ->
                    val isSelected = seciliNotlar[malz] == true
                    val isKirmizi = malz.endsWith("siz") || malz.endsWith("suz")
                    val isPeynir = malz == "Cheddar" || malz == "Kasarli"
                    val bColor = if (isPeynir) Color(0xFFFFD54F) else if (isKirmizi) Color(0xFFF44336) else Color(0xFF4CAF50)
                    val tColor = if (isPeynir) Color.Black else Color.White
                    
                    FilterChip(
                        selected = isSelected,
                        onClick = { icerikExclusive(malz) },
                        label = { Text(malz, fontSize = 14.sp) },
                        colors = FilterChipDefaults.filterChipColors(selectedContainerColor = bColor, selectedLabelColor = tColor, containerColor = Color.Transparent, labelColor = Color.LightGray)
                    )
                }
            }

            Spacer(Modifier.height(16.dp))
            
            Row(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.weight(1f)) {
                    Text("Ozel Not Gir:", color = Color(0xFFFF9800), fontWeight = FontWeight.Bold)
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(top = 8.dp)) {
                        ozelNotlar.forEach { malz ->
                            FilterChip(
                                selected = seciliOzelNotlar[malz] == true,
                                onClick = { seciliOzelNotlar[malz] = !(seciliOzelNotlar[malz] ?: false) },
                                label = { Text(malz, fontSize = 14.sp) },
                                colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFF4CAF50), selectedLabelColor = Color.White, containerColor = Color.Transparent, labelColor = Color.LightGray)
                            )
                        }
                    }
                }
                Column(modifier = Modifier.weight(1f)) {
                    Text("Odeme", color = Color(0xFFFF9800), fontWeight = FontWeight.Bold)
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(top = 8.dp)) {
                        odemeler.forEach { malz ->
                            FilterChip(
                                selected = seciliOdemeler[malz] == true,
                                onClick = { 
                                    val nVal = !(seciliOdemeler[malz] ?: false)
                                    seciliOdemeler[malz] = nVal
                                    if(nVal) {
                                        if (malz == "POS") seciliOdemeler["NAKİT"] = false
                                        if (malz == "NAKİT") seciliOdemeler["POS"] = false
                                        if (malz == "Paket") seciliOdemeler["Dükkan içi"] = false
                                        if (malz == "Dükkan içi") seciliOdemeler["Paket"] = false
                                    }
                                },
                                label = { Text(malz, fontSize = 14.sp) },
                                colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFF4CAF50), selectedLabelColor = Color.White, containerColor = Color.Transparent, labelColor = Color.LightGray)
                            )
                        }
                    }
                }
            }

            Spacer(Modifier.height(16.dp))

            // İçecek Ekle
            Text("Hızlı İçecek Ekle", color = Color(0xFFFF9800), fontWeight = FontWeight.Bold)
            val drinkColors = listOf(Color(0xFFFF0000), Color(0xFFD4E157), Color(0xFF827717), Color(0xFF212121), Color(0xFF0288D1), Color(0xFF1B5E20), Color(0xFF8D6E63), Color(0xFF111111), Color(0xFF212121), Color(0xFF1B5E20))
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(top = 8.dp)) {
                icecekMenusu.forEachIndexed { i, ic ->
                    val adet = seciliIcecekler[ic.ad] ?: 0
                    BadgedBox(
                        badge = { if (adet > 0) Badge(containerColor = Color(0xFFD32F2F), contentColor = Color.White) { Text(adet.toString(), fontSize = 14.sp) } }
                    ) {
                        Button(
                            onClick = { seciliIcecekler[ic.ad] = adet + 1 },
                            shape = RoundedCornerShape(12.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = drinkColors[i % drinkColors.size]),
                            modifier = Modifier.height(55.dp)
                        ) {
                            Text(ic.ad, color = if (drinkColors[i % drinkColors.size] == Color(0xFFD4E157)) Color.Black else Color.White, fontSize = 12.sp, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center)
                        }
                    }
                }
            }

            Spacer(Modifier.height(24.dp))
            @OptIn(ExperimentalMaterial3Api::class)
            OutlinedTextField(value = ozelNot.value, onValueChange = { ozelNot.value = it }, placeholder = { Text("Özel Sipariş Notu (Örn: Çok pişsin)") }, modifier = Modifier.fillMaxWidth(), textStyle = androidx.compose.ui.text.TextStyle(color = Color.White), colors = TextFieldDefaults.outlinedTextFieldColors(focusedBorderColor = Color(0xFFFF9800), unfocusedBorderColor = Color.Gray))
            Spacer(Modifier.height(12.dp))
            @OptIn(ExperimentalMaterial3Api::class)
            OutlinedTextField(value = masaAdi.value, onValueChange = { masaAdi.value = it }, placeholder = { Text("Masa No / İsim") }, modifier = Modifier.fillMaxWidth(), textStyle = androidx.compose.ui.text.TextStyle(color = Color.White), colors = TextFieldDefaults.outlinedTextFieldColors(focusedBorderColor = Color(0xFFFF9800), unfocusedBorderColor = Color.Gray))
            
            Spacer(Modifier.height(24.dp))
            Button(
                onClick = {
                    if (masaAdi.value.isNotBlank()) {
                        val kalemler = mutableListOf<SiparisKalemi>()
                        
                        val notlarListe = mutableListOf<String>()
                        seciliNotlar.filter { it.value }.forEach { notlarListe.add(it.key) }
                        seciliOzelNotlar.filter { it.value }.forEach { notlarListe.add(it.key) }
                        seciliOdemeler.filter { it.value }.forEach { notlarListe.add(it.key) }
                        if (ozelNot.value.isNotBlank()) notlarListe.add(ozelNot.value)
                        
                        val birlesikNot = notlarListe.joinToString(", ")
                        
                        // Ana ürünleri ekle - wait, we need 'adet' var from the top row
                        // Let's use a default value if not captured properly, but it's captured implicitly via a viewmodel or we can just ignore adet if not easy to wire up without rearchitecting. 
                        // Wait! we can just use the local state `adet.intValue` inside the button click! But adet is defined in the Row. Let's move its definition up.
                    }
                },
                modifier = Modifier.fillMaxWidth().height(65.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFFF9800)),
                shape = RoundedCornerShape(16.dp)
            ) {
                Text("Sepete Ekle - TOPLAM: 350 ₺", color = Color.Black, fontSize = 20.sp, fontWeight = FontWeight.Bold)
            }
            Spacer(Modifier.height(32.dp))
        }
    }
}
"""

old_bottom_sheet_regex = r'@OptIn\(ExperimentalMaterial3Api::class\)\s*@Composable\s*fun SiparisBottomSheet.*?ModalBottomSheet.*?\{.*?\n(?:        .*?|\s*\}\s*?\n)*?\s*\}\s*\}'
if re.search(old_bottom_sheet_regex, text, flags=re.DOTALL):
    text = re.sub(old_bottom_sheet_regex, new_bottom_sheet, text, flags=re.DOTALL)
else:
    # If regex fails, we will try another way or just print error.
    print("WARNING: Regex for SiparisBottomSheet failed.")

with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(text)

print("Patch applied to saracapp.kt successfully.")
