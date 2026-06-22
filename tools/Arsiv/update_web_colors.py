import os
import codecs

app_js = 'C:/Users/bilal/SARACAPP/static/app.js'
with codecs.open(app_js, 'r', 'utf-8') as f:
    text = f.read()

# Fix Card Colors
old_color_func = '''function getCardColorClass(name) {
    name = name.toLowerCase();
    if (name.includes("tombik")) return "orange";
    if (name.includes("eski usul")) return "red";
    if (name.includes("dürüm")) return "yellow";
    return "";
}'''

new_color_func = '''function getCardColorClass(name) {
    name = name.toLowerCase();
    if (name.includes("et porsiyon") || name.includes("pilav üstü beyti") || name.includes("iskender")) return "dark-red";
    if (name.includes("tavuk hatay usulü")) return "cream";
    if (name.includes("biga döner")) return "blue";
    if (name.includes("tavuk porsiyon") || name.includes("pilav üstü")) return "dark-orange";
    if (name.includes("tombik")) return "orange";
    if (name.includes("eski usul")) return "red";
    if (name.includes("dürüm")) return "yellow";
    return "";
}

function getDrinkColorClass(name) {
    name = name.toLowerCase();
    if (name.includes("coca cola") || name.includes("şişe kola") || name.includes("kutu kola") || name.includes("cola zero")) return "cola-red";
    if (name.includes("sprite")) return "sprite-green";
    if (name.includes("fanta")) return "fanta-yellow";
    if (name.includes("ayran")) return "ayran-white";
    if (name.includes("su") && !name.includes("şalgam")) return "water-blue";
    if (name.includes("soda")) return "soda-green";
    if (name.includes("şalgam")) return "salgam-purple";
    return "";
}'''

text = text.replace(old_color_func, new_color_func)

# Fix Drinks Rendering
old_drink_render = '''                const dBtn = document.createElement('button');
                dBtn.className = 'drink-btn';'''

new_drink_render = '''                const dBtn = document.createElement('button');
                dBtn.className = 'drink-btn ' + getDrinkColorClass(ic.ad);'''

text = text.replace(old_drink_render, new_drink_render)

# Fix -siz/-suz suffix
old_chip = '''        if (isNegative) label += " Yok";'''

new_chip = '''        if (isNegative) {
            let n = label;
            label = n + "sız";
            if (n === "Soğan") label = "Soğansız";
            if (n === "Domates") label = "Domatessiz";
            if (n === "Patates") label = "Patatessiz";
            if (n === "Ketçap") label = "Ketçapsız";
            if (n === "Mayonez") label = "Mayonezsiz";
            if (n === "Turşu") label = "Turşusuz";
        } else if (containerId === 'icerikCikarContainer') {
            let n = label;
            label = n + "lı";
            if (n === "Soğan") label = "Soğanlı";
            if (n === "Domates") label = "Domatesli";
            if (n === "Patates") label = "Patatesli";
            if (n === "Ketçap") label = "Ketçaplı";
            if (n === "Mayonez") label = "Mayonezli";
            if (n === "Turşu") label = "Turşulu";
        }'''

text = text.replace(old_chip, new_chip)

with codecs.open(app_js, 'w', 'utf-8') as f:
    f.write(text)

style_css = 'C:/Users/bilal/SARACAPP/static/style.css'
with codecs.open(style_css, 'r', 'utf-8') as f:
    stext = f.read()

colors_css = '''
/* Custom Card Colors */
.card.dark-red { background: #8B0000; color: white; }
.card.dark-red .card-price { color: #FFD700; }
.card.cream { background: #FFFDD0; color: black; }
.card.cream .card-price { color: #8B0000; }
.card.blue { background: #2196F3; color: white; }
.card.blue .card-price { color: #FFEB3B; }
.card.dark-orange { background: #E65100; color: white; }
.card.dark-orange .card-price { color: #FFD54F; }

/* Drink Buttons Colors */
.drink-btn.cola-red { background: #F40009; color: white; }
.drink-btn.cola-red.selected { background: #B71C1C; color: white; border: 2px solid white; }
.drink-btn.sprite-green { background: #008B47; color: white; }
.drink-btn.sprite-green.selected { background: #004D40; color: white; border: 2px solid white; }
.drink-btn.fanta-yellow { background: #F7941E; color: black; }
.drink-btn.fanta-yellow.selected { background: #F57F17; color: black; border: 2px solid black; }
.drink-btn.ayran-white { background: #F5F5DC; color: black; }
.drink-btn.ayran-white.selected { background: #D7CCC8; color: black; border: 2px solid black; }
.drink-btn.water-blue { background: #00BFFF; color: black; }
.drink-btn.water-blue.selected { background: #0277BD; color: white; border: 2px solid white; }
.drink-btn.soda-green { background: #006400; color: white; }
.drink-btn.soda-green.selected { background: #1B5E20; color: white; border: 2px solid white; }
.drink-btn.salgam-purple { background: #800080; color: white; }
.drink-btn.salgam-purple.selected { background: #4A148C; color: white; border: 2px solid white; }
'''

if 'dark-red' not in stext:
    stext = stext + colors_css
    with codecs.open(style_css, 'w', 'utf-8') as f:
        f.write(stext)

print("Updated app.js and style.css")
