import codecs
import re

filepath = 'C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

old_flow = 'FlowRow(modifier = Modifier.fillMaxWidth().padding(top = 8.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalArrangement = Arrangement.spacedBy(12.dp), maxItemsInEachRow = 3) {'
new_flow = '''val currentViewConfig = androidx.compose.ui.platform.LocalViewConfiguration.current
                val fastLongPressConfig = androidx.compose.runtime.remember(currentViewConfig) {
                    object : androidx.compose.ui.platform.ViewConfiguration by currentViewConfig {
                        override val longPressTimeoutMillis: Long = 200L
                    }
                }
                androidx.compose.runtime.CompositionLocalProvider(androidx.compose.ui.platform.LocalViewConfiguration provides fastLongPressConfig) {
                FlowRow(modifier = Modifier.fillMaxWidth().padding(top = 8.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalArrangement = Arrangement.spacedBy(12.dp), maxItemsInEachRow = 3) {'''

# Find the closing
pattern_closing = r'(\s+)\}\s+\}\s+\}\s+\}\s+Spacer\(modifier = Modifier\.height\(8\.dp\)\)\s+OutlinedTextField'
if re.search(pattern_closing, text):
    # we need to add one more '}' to close CompositionLocalProvider
    replacement = r'\1}\n\1    }\n\1}\n\1}\n\1}\n            Spacer(modifier = Modifier.height(8.dp))\n            OutlinedTextField'
    text = re.sub(pattern_closing, replacement, text)
    text = text.replace(old_flow, new_flow)
    print("Wrapped FlowRow with CompositionLocalProvider")
else:
    print("Could not find closing block")

with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(text)
