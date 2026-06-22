import codecs
with codecs.open('C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt', 'r', 'utf-8') as f:
    text = f.read()

# Fix the broken braces
if 'kalemSilClick(tekliKalem) }\n                            }, contentAlignment = Alignment.Center)' in text:
    text = text.replace('kalemSilClick(tekliKalem) }\n                            }, contentAlignment = Alignment.Center) { Text("🗑️", fontSize = 16.sp) }\n                            }\n                                    }\n                                }\n                            }\n                        }', 'kalemSilClick(tekliKalem) }, contentAlignment = Alignment.Center) { Text("🗑️", fontSize = 16.sp) }\n                                    }\n                                }\n                            }\n                            }\n                        }')

with codecs.open('C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt', 'w', 'utf-8') as f:
    f.write(text)
