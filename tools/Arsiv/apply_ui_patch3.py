import codecs
import re

filepath = 'C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

# 1. Update Gramaj FlowRow
old_gramaj = '''Text("Seçim / Gramaj", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary, fontSize = 15.sp)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.padding(top = 8.dp)) {
                urun.secenekler.forEach { sec -> FilterChip(selected = (seciliGramaj == sec), onClick = { seciliGramaj = sec }, label = { Text(if(sec.gramaj == "Standart") " ₺" else " (₺)", fontSize = 15.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(6.dp)) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFF4CAF50), selectedLabelColor = Color.White)) }
            }'''
new_gramaj = '''Text("Seçim / Gramaj", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary, fontSize = 15.sp)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.padding(top = 4.dp)) {
                urun.secenekler.forEach { sec -> FilterChip(selected = (seciliGramaj == sec), onClick = { seciliGramaj = sec }, label = { Text(if(sec.gramaj == "Standart") " ₺" else " (₺)", fontSize = 13.sp, fontWeight = FontWeight.Bold) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Color(0xFF4CAF50), selectedLabelColor = Color.White)) }
            }'''

# Replace Gramaj block
if "Text(\"Seçim / Gramaj\"" in text:
    # use regex because of encoding/newlines
    pattern_gramaj = r'Text\("Seçim / Gramaj".*?FlowRow.*?urun\.secenekler\.forEach.*?\}\s+\}'
    if re.search(pattern_gramaj, text, re.DOTALL):
        text = re.sub(pattern_gramaj, new_gramaj, text, flags=re.DOTALL)
        print("Gramaj replaced via regex")

# 2. Update Icecek Layout & Gesture
old_icecek_flow = 'FlowRow(modifier = Modifier.fillMaxWidth().padding(top = 8.dp), horizontalArrangement = Arrangement.spacedBy(12.dp), verticalArrangement = Arrangement.spacedBy(12.dp))'
new_icecek_flow = 'FlowRow(modifier = Modifier.fillMaxWidth().padding(top = 8.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalArrangement = Arrangement.spacedBy(12.dp), maxItemsInEachRow = 3)'
text = text.replace(old_icecek_flow, new_icecek_flow)

old_box_size = '.size(85.dp, 55.dp)'
new_box_size = '.height(55.dp).width(110.dp)'
text = text.replace(old_box_size, new_box_size)

# Custom Fast Long Press Gesture Replacement
# We need to replace the .combinedClickable(...) block
old_clickable_pattern = r'\.combinedClickable\(\s*onClick = \{.*?\},\s*onLongClick = \{.*?\}\s*\)'

new_clickable = '''.pointerInput(Unit) {
                                        androidx.compose.foundation.gestures.detectTapGestures(
                                            onPress = {
                                                val pressStartTime = System.currentTimeMillis()
                                                val job = kotlinx.coroutines.GlobalScope.launch(kotlinx.coroutines.Dispatchers.Main) {
                                                    kotlinx.coroutines.delay(200) // Hızlı uzun basma süresi
                                                    if (miktar > 0) {
                                                        haptic.performHapticFeedback(androidx.compose.ui.hapticfeedback.HapticFeedbackType.LongPress)
                                                        if (miktar == 1) {
                                                            seciliIcecekler[ic.ad] = false
                                                            icecekAdetleri[ic.ad] = 1
                                                        } else {
                                                            icecekAdetleri[ic.ad] = miktar - 1
                                                        }
                                                    }
                                                }
                                                val success = tryAwaitRelease()
                                                if (success) {
                                                    if (System.currentTimeMillis() - pressStartTime < 200) {
                                                        job.cancel()
                                                        haptic.performHapticFeedback(androidx.compose.ui.hapticfeedback.HapticFeedbackType.TextHandleMove)
                                                        if (miktar == 0) {
                                                            seciliIcecekler[ic.ad] = true
                                                            icecekAdetleri[ic.ad] = 1
                                                        } else {
                                                            icecekAdetleri[ic.ad] = miktar + 1
                                                        }
                                                    }
                                                } else {
                                                    job.cancel()
                                                }
                                            }
                                        )
                                    }'''

if re.search(old_clickable_pattern, text, re.DOTALL):
    text = re.sub(old_clickable_pattern, new_clickable, text, flags=re.DOTALL)
    print("Clickable replaced via regex")

with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(text)
print("Patch executed.")
