import codecs
import re

filepath = 'C:/Users/bilal/AndroidStudioProjects/saracapp/app/src/main/java/com/bilalgnd/saracapp/saracapp.kt'
with codecs.open(filepath, 'r', 'utf-8') as f:
    text = f.read()

# Fix the trailing braces syntax error
old_trailing = '''                                        }
                                    )
                                    },
                                contentAlignment = Alignment.Center'''
new_trailing = '''                                        }
                                    ),
                                contentAlignment = Alignment.Center'''
text = text.replace(old_trailing, new_trailing)

# Apply CompositionLocalProvider correctly around the FlowRow
old_flow = 'FlowRow(modifier = Modifier.fillMaxWidth().padding(top = 8.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalArrangement = Arrangement.spacedBy(12.dp), maxItemsInEachRow = 3) {'
new_flow = '''val currentViewConfig = androidx.compose.ui.platform.LocalViewConfiguration.current
                val fastLongPressConfig = remember(currentViewConfig) {
                    object : androidx.compose.ui.platform.ViewConfiguration by currentViewConfig {
                        override val longPressTimeoutMillis: Long = 200L
                    }
                }
                androidx.compose.runtime.CompositionLocalProvider(androidx.compose.ui.platform.LocalViewConfiguration provides fastLongPressConfig) {
                FlowRow(modifier = Modifier.fillMaxWidth().padding(top = 8.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalArrangement = Arrangement.spacedBy(12.dp), maxItemsInEachRow = 3) {'''

# Find the exact ending to close CompositionLocalProvider
# Look for the end of the FlowRow, which is followed by if (!isIcecek) closing brace or Spacer
# From line 638:
# 638:                 }
# 639:             }
# 640: 
# 641:             Spacer(modifier = Modifier.height(12.dp))
old_closing = '''                            }
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(12.dp))
            OutlinedTextField('''

new_closing = '''                            }
                        }
                    }
                }
                } // End of CompositionLocalProvider
            }

            Spacer(modifier = Modifier.height(12.dp))
            OutlinedTextField('''

if old_closing in text:
    text = text.replace(old_closing, new_closing)
    text = text.replace(old_flow, new_flow)
    print("CompositionLocalProvider applied successfully.")
else:
    # Let's try more flexible matching
    pattern_closing = r'(\s+)\}\s+\}\s+\}\s+\}\s+Spacer\(modifier = Modifier\.height\(12\.dp\)\)\s+OutlinedTextField'
    if re.search(pattern_closing, text):
        replacement = r'\1}\n\1}\n\1}\n\1}\n\1}\n\1}\n            Spacer(modifier = Modifier.height(12.dp))\n            OutlinedTextField'
        text = re.sub(pattern_closing, replacement, text)
        print("Regex replaced closing")
    else:
        print("Could not find closing block.")

with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(text)
print("Fix executed.")
