import codecs

with codecs.open('C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt', 'r', 'utf-8') as f:
    lines = f.readlines()

for i in range(len(lines)):
    if 'import androidx.compose.runtime.remember' in lines[i] and 'import androidx.compose.runtime.key' not in ''.join(lines):
        lines.insert(i+1, 'import androidx.compose.runtime.key\n')
        break

for i in range(len(lines)):
    if 'kalemListesi.forEach { tekliKalem ->' in lines[i]:
        # Insert key(System.identityHashCode(tekliKalem)) { 
        lines[i] = lines[i].replace('kalemListesi.forEach { tekliKalem ->', 'kalemListesi.forEach { tekliKalem ->\n                            key(System.identityHashCode(tekliKalem)) {')
        # find the closing brace for this forEach
        # It's at line + 13 or so. Let's just indent the next 12 lines
        for j in range(i+1, i+14):
            if '}' in lines[j] and '}' in lines[j+1] and '}' in lines[j+2]:
                lines[j] = lines[j].replace('}', '}\n                            }')
                break
        break

with codecs.open('C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt', 'w', 'utf-8') as f:
    f.writelines(lines)
print("Patch applied.")
