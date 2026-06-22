import codecs
import re

filepath = 'C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

# Restore old combinedClickable
bad_clickable = r'\.pointerInput\(Unit\) \{\s*androidx\.compose\.foundation\.gestures\.detectTapGestures.*?\n\s*\}\s*\)'

good_clickable = '''.combinedClickable(
                                        onClick = { 
                                            haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                                            if (miktar == 0) {
                                                seciliIcecekler[ic.ad] = true
                                                icecekAdetleri[ic.ad] = 1
                                            } else {
                                                icecekAdetleri[ic.ad] = miktar + 1
                                            }
                                        },
                                        onLongClick = { 
                                            if (miktar > 0) {
                                                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                                                if (miktar == 1) {
                                                    seciliIcecekler[ic.ad] = false
                                                    icecekAdetleri[ic.ad] = 1
                                                } else {
                                                    icecekAdetleri[ic.ad] = miktar - 1
                                                }
                                            }
                                        }
                                    )'''

if re.search(bad_clickable, text, re.DOTALL):
    text = re.sub(bad_clickable, good_clickable, text, flags=re.DOTALL)
    print("Reverted to combinedClickable")
else:
    print("Could not find bad clickable")

# Now wrap FlowRow with CompositionLocalProvider
# FlowRow starts at: FlowRow(modifier = Modifier.fillMaxWidth().padding(top = 8.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalArrangement = Arrangement.spacedBy(12.dp), maxItemsInEachRow = 3) {
old_flow = 'FlowRow(modifier = Modifier.fillMaxWidth().padding(top = 8.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalArrangement = Arrangement.spacedBy(12.dp), maxItemsInEachRow = 3) {'
new_flow = '''val currentViewConfig = androidx.compose.ui.platform.LocalViewConfiguration.current
                val fastLongPressConfig = remember(currentViewConfig) {
                    object : androidx.compose.ui.platform.ViewConfiguration by currentViewConfig {
                        override val longPressTimeoutMillis: Long = 200L
                    }
                }
                androidx.compose.runtime.CompositionLocalProvider(androidx.compose.ui.platform.LocalViewConfiguration provides fastLongPressConfig) {
                FlowRow(modifier = Modifier.fillMaxWidth().padding(top = 8.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalArrangement = Arrangement.spacedBy(12.dp), maxItemsInEachRow = 3) {'''

# Find the closing brace of FlowRow to close CompositionLocalProvider
# This is after the drink boxes.
# The structure is: 
# FlowRow { icecekMenusu.forEach { ... } }
# }
# Spacer(modifier = Modifier.height(12.dp))
# OutlinedTextField(...)

pattern_closing = r'(FlowRow\(modifier = Modifier\.fillMaxWidth.*?\}\s+)\}\s+Spacer\(modifier = Modifier\.height\(12\.dp\)\)'
if re.search(pattern_closing, text, re.DOTALL):
    replacement = r'\1}\n                }\n                Spacer(modifier = Modifier.height(12.dp))'
    text = re.sub(pattern_closing, replacement, text, count=1, flags=re.DOTALL)
    text = text.replace(old_flow, new_flow)
    print("Wrapped FlowRow with CompositionLocalProvider")

with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(text)
print("Fix applied.")
