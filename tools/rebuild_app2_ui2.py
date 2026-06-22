import codecs

filepath = r'C:\Users\bilal\SARACAPP\saracapp2\app\src\main\java\com\bilalgnd\saracapp\saracapp.kt'
with codecs.open(filepath, 'r', 'utf-8') as f:
    lines = f.readlines()

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

    val adet = remember { mutableIntStateOf(1) }

    fun hesapla(): Int {
        var top = anlikFiyat.intValue
        seciliNotlar.forEach { (k, v) -> if (v && ucretliEkstralar.containsKey(k)) top += ucretliEkstralar[k]!! }
        seciliIcecekler.forEach { (ad, adtt) -> 
            val icFiyat = icecekMenusu.find { it.ad == ad }?.secenekler?.firstOrNull()?.fiyat ?: 0
            top += (icFiyat * adtt)
        }
        return top
    }

    ModalBottomSheet(onDismissRequest = kapat, sheetState = sheetState, containerColor = Color(0xFF1E1E1E)) {
        Column(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp).verticalScroll(rememberScrollState())) {
            
            // Header
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Text(urun.ad, color = Color.White, fontSize = 28.sp, fontWeight = FontWeight.Bold)
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
                    val adt = seciliIcecekler[ic.ad] ?: 0
                    BadgedBox(
                        badge = { if (adt > 0) Badge(containerColor = Color(0xFFD32F2F), contentColor = Color.White) { Text(adt.toString(), fontSize = 14.sp) } }
                    ) {
                        Button(
                            onClick = { seciliIcecekler[ic.ad] = adt + 1 },
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
                        
                        // Ana ürünleri ekle
                        for (j in 0 until adet.intValue) {
                            kalemler.add(SiparisKalemi(urun.ad, seciliGramaj.value, anlikFiyat.intValue, birlesikNot))
                        }
                        
                        // İçecekleri ekle
                        seciliIcecekler.filter { it.value > 0 }.forEach { (icAd, icAdet) ->
                            val icUrun = icecekMenusu.find { it.ad == icAd }
                            if (icUrun != null) {
                                val icFiyat = icUrun.secenekler.firstOrNull()?.fiyat ?: 0
                                for (j in 0 until icAdet) {
                                    kalemler.add(SiparisKalemi(icAd, "Standart", icFiyat, ""))
                                }
                            }
                        }
                        
                        onSiparisEkle(masaAdi.value.trim(), kalemler)
                        kapat()
                    }
                },
                modifier = Modifier.fillMaxWidth().height(65.dp),
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFFF9800)),
                shape = RoundedCornerShape(16.dp)
            ) {
                Text("Sepete Ekle - TOPLAM: ${hesapla() * adet.intValue} ₺", color = Color.Black, fontSize = 20.sp, fontWeight = FontWeight.Bold)
            }
            Spacer(Modifier.height(32.dp))
        }
    }
}
"""

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if "fun SiparisBottomSheet(" in line and "@Composable" in lines[i-1]:
        start_idx = i - 1
        if "@OptIn" in lines[i-2]:
            start_idx = i - 2
    if "fun AdisyonKarti(" in line:
        end_idx = i - 1
        if "@Composable" in lines[i-1]:
            end_idx = i - 2
        break

if start_idx != -1 and end_idx != -1:
    new_lines = lines[:start_idx] + [new_bottom_sheet] + lines[end_idx:]
    with codecs.open(filepath, 'w', 'utf-8') as f:
        f.writelines(new_lines)
    print("SiparisBottomSheet replaced successfully.")
else:
    print(f"Could not find boundaries! start_idx={start_idx}, end_idx={end_idx}")
