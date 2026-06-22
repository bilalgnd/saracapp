import codecs

filepath = 'C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

# 1. Fix Gramaj string interpolation
old_gramaj_text = 'Text(if(sec.gramaj == "Standart") " ₺" else " (₺)", fontSize = 13.sp, fontWeight = FontWeight.Bold)'
new_gramaj_text = 'Text(if(sec.gramaj == "Standart") " ₺" else " (₺)", fontSize = 13.sp, fontWeight = FontWeight.Bold)'
text = text.replace(old_gramaj_text, new_gramaj_text)

# 2. Update Icecek Layout to fit in 2 rows
# maxItemsInEachRow = 3 -> 5
text = text.replace('maxItemsInEachRow = 3', 'maxItemsInEachRow = 5')

# .height(55.dp).width(110.dp) -> .height(50.dp).width(68.dp)
text = text.replace('.height(55.dp).width(110.dp)', '.height(50.dp).width(68.dp)')

# fontSize = 13.sp -> 11.sp for drink text
text = text.replace('Text(ic.ad, color = Color.White, fontSize = 13.sp, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center, modifier = Modifier.padding(4.dp))', 'Text(ic.ad, color = Color.White, fontSize = 11.sp, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center, modifier = Modifier.padding(2.dp), lineHeight = 12.sp)')

with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(text)
print("Patch executed successfully.")
