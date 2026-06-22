import codecs

with codecs.open('C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt', 'r', 'utf-8') as f:
    content = f.read()

# Add import if missing
if 'import androidx.compose.runtime.key' not in content:
    content = content.replace('import androidx.compose.runtime.remember', 'import androidx.compose.runtime.remember\nimport androidx.compose.runtime.key')

old_code = '''                        kalemListesi.forEach { tekliKalem ->
                            val dismissState = rememberSwipeToDismissBoxState(confirmValueChange = { if (it == SwipeToDismissBoxValue.EndToStart) { kalemSilClick(tekliKalem); true } else false })
                            SwipeToDismissBox(state = dismissState, enableDismissFromStartToEnd = false, backgroundContent = { val color by animateColorAsState(if (dismissState.targetValue == SwipeToDismissBoxValue.EndToStart) Color.Red else Color.Transparent); Box(Modifier.fillMaxSize().background(color).padding(horizontal = 20.dp), contentAlignment = Alignment.CenterEnd) { Text("Sil", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 18.sp) } }) {
                                Row(modifier = Modifier.fillMaxWidth().background(Color(0xFF1E1E1E)).padding(horizontal = 16.dp, vertical = 12.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                                    Text(text = "↳ 1x ", fontSize = 16.sp, color = Color.LightGray)
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        Text(text = " ₺", fontSize = 16.sp, color = Color.Gray, modifier = Modifier.padding(end = 12.dp))
                                        Box(modifier = Modifier.size(36.dp).background(Color(0xFF333333), RoundedCornerShape(8.dp)).clickable { notDuzenleClick(tekliKalem) }, contentAlignment = Alignment.Center) { Text("✏️", fontSize = 16.sp) }
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Box(modifier = Modifier.size(36.dp).background(Color(0xFF421515), RoundedCornerShape(8.dp)).clickable { kalemSilClick(tekliKalem) }, contentAlignment = Alignment.Center) { Text("🗑️", fontSize = 16.sp) }
                                    }
                                }
                            }
                        }'''

new_code = '''                        kalemListesi.forEach { tekliKalem ->
                            key(System.identityHashCode(tekliKalem)) {
                                val dismissState = rememberSwipeToDismissBoxState(confirmValueChange = { if (it == SwipeToDismissBoxValue.EndToStart) { kalemSilClick(tekliKalem); true } else false })
                                SwipeToDismissBox(state = dismissState, enableDismissFromStartToEnd = false, backgroundContent = { val color by animateColorAsState(if (dismissState.targetValue == SwipeToDismissBoxValue.EndToStart) Color.Red else Color.Transparent); Box(Modifier.fillMaxSize().background(color).padding(horizontal = 20.dp), contentAlignment = Alignment.CenterEnd) { Text("Sil", color = Color.White, fontWeight = FontWeight.Bold, fontSize = 18.sp) } }) {
                                    Row(modifier = Modifier.fillMaxWidth().background(Color(0xFF1E1E1E)).padding(horizontal = 16.dp, vertical = 12.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                                        Text(text = "↳ 1x ", fontSize = 16.sp, color = Color.LightGray)
                                        Row(verticalAlignment = Alignment.CenterVertically) {
                                            Text(text = " ₺", fontSize = 16.sp, color = Color.Gray, modifier = Modifier.padding(end = 12.dp))
                                            Box(modifier = Modifier.size(36.dp).background(Color(0xFF333333), RoundedCornerShape(8.dp)).clickable { notDuzenleClick(tekliKalem) }, contentAlignment = Alignment.Center) { Text("✏️", fontSize = 16.sp) }
                                            Spacer(modifier = Modifier.width(8.dp))
                                            Box(modifier = Modifier.size(36.dp).background(Color(0xFF421515), RoundedCornerShape(8.dp)).clickable { kalemSilClick(tekliKalem) }, contentAlignment = Alignment.Center) { Text("🗑️", fontSize = 16.sp) }
                                        }
                                    }
                                }
                            }
                        }'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with codecs.open('C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt', 'w', 'utf-8') as f:
        f.write(content)
    print("Replaced successfully.")
else:
    print("Could not find old code.")
