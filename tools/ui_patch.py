import os

path = r'C:\Users\bilal\SARACAPP\saracapp_ui.py'
with open(path, 'r', encoding='utf-8') as f: 
    content = f.read()

# Fix window sizes for lower resolution screens
content = content.replace('self.geometry("1400x800")', 'self.geometry("1024x720")')
content = content.replace('self.minsize(1300, 700)', 'self.minsize(1024, 600)')

# Use modern Windows font Segoe UI instead of Arial
content = content.replace('"Arial"', '"Segoe UI"')

# Make the right panel slightly wider so text doesn't clip on small screens
content = content.replace('self.grid_columnconfigure(0, weight=65)', 'self.grid_columnconfigure(0, weight=60)')
content = content.replace('self.grid_columnconfigure(1, weight=35, minsize=400)', 'self.grid_columnconfigure(1, weight=40, minsize=450)')

with open(path, 'w', encoding='utf-8') as f: 
    f.write(content)
print('UI scaling and fonts modernized.')
