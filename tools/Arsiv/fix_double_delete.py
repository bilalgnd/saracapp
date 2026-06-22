import codecs

filepath = 'C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

# Add import if missing
if 'import androidx.compose.runtime.mutableStateOf' not in text:
    text = text.replace('import androidx.compose.runtime.remember', 'import androidx.compose.runtime.remember\nimport androidx.compose.runtime.mutableStateOf\nimport androidx.compose.runtime.getValue\nimport androidx.compose.runtime.setValue')

old_line = 'val dismissState = rememberSwipeToDismissBoxState(confirmValueChange = { if (it == SwipeToDismissBoxValue.EndToStart) { kalemSilClick(tekliKalem); true } else false })'
new_line = '''var isDeleted by remember { mutableStateOf(false) }
                                val dismissState = rememberSwipeToDismissBoxState(confirmValueChange = { 
                                    if (it == SwipeToDismissBoxValue.EndToStart) {
                                        if (!isDeleted) {
                                            isDeleted = true
                                            kalemSilClick(tekliKalem)
                                        }
                                        true 
                                    } else false 
                                })'''

if old_line in text:
    text = text.replace(old_line, new_line)
    with codecs.open(filepath, 'w', 'utf-8') as f:
        f.write(text)
    print("Replaced successfully")
else:
    print("Old line not found")
