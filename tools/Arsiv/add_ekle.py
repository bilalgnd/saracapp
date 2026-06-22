import codecs

app_js = 'C:/Users/bilal/SARACAPP/static/app.js'
with codecs.open(app_js, 'r', 'utf-8') as f:
    text = f.read()

# 1. Add seciliEklenecekler state
text = text.replace('let seciliNotlar = {};', 'let seciliNotlar = {};\nlet seciliEklenecekler = {};')

# 2. Update renderChipGroup
old_render = '''        } else if (containerId === 'icerikCikarContainer') {
            let n = label;
            label = n + "lı";
            if (n === "Soğan") label = "Soğanlı";
            if (n === "Domates") label = "Domatesli";
            if (n === "Patates") label = "Patatesli";
            if (n === "Ketçap") label = "Ketçaplı";
            if (n === "Mayonez") label = "Mayonezli";
            if (n === "Turşu") label = "Turşulu";
        }'''

new_render = '''        } else if (containerId === 'icerikEkleContainer') {
            let n = label;
            label = n + "lı";
            if (n === "Soğan") label = "Soğanlı";
            if (n === "Domates") label = "Domatesli";
            if (n === "Patates") label = "Patatesli";
            if (n === "Ketçap") label = "Ketçaplı";
            if (n === "Mayonez") label = "Mayonezli";
            if (n === "Turşu") label = "Turşulu";
        }'''

text = text.replace(old_render, new_render)

# 3. Add to openProductSheet
old_open = '''        renderChipGroup('icerikCikarContainer', malzemeler_listesi, seciliNotlar, true, 'chip-red');'''

new_open = '''        renderChipGroup('icerikCikarContainer', malzemeler_listesi, seciliNotlar, true, 'chip-red');
        seciliEklenecekler = {};
        renderChipGroup('icerikEkleContainer', malzemeler_listesi, seciliEklenecekler, false, 'chip-yellow');'''

text = text.replace(old_open, new_open)

# 4. Add seciliEklenecekler to addProductToDraft tumNotlar
old_draft = '''    Object.keys(seciliNotlar).forEach(k => { 
        if(seciliNotlar[k]) {
            let label = k + "sız";
            if (k === "Soğan") label = "Soğansız";
            if (k === "Domates") label = "Domatessiz";
            if (k === "Patates") label = "Patatessiz";
            if (k === "Ketçap") label = "Ketçapsız";
            if (k === "Mayonez") label = "Mayonezsiz";
            if (k === "Turşu") label = "Turşusuz";
            tumNotlar.push(label); 
        } 
    });'''

new_draft = '''    Object.keys(seciliNotlar).forEach(k => { 
        if(seciliNotlar[k]) {
            let label = k + "sız";
            if (k === "Soğan") label = "Soğansız";
            if (k === "Domates") label = "Domatessiz";
            if (k === "Patates") label = "Patatessiz";
            if (k === "Ketçap") label = "Ketçapsız";
            if (k === "Mayonez") label = "Mayonezsiz";
            if (k === "Turşu") label = "Turşusuz";
            tumNotlar.push(label); 
        } 
    });
    Object.keys(seciliEklenecekler).forEach(k => { 
        if(seciliEklenecekler[k]) {
            let label = k + "lı";
            if (k === "Soğan") label = "Soğanlı";
            if (k === "Domates") label = "Domatesli";
            if (k === "Patates") label = "Patatesli";
            if (k === "Ketçap") label = "Ketçaplı";
            if (k === "Mayonez") label = "Mayonezli";
            if (k === "Turşu") label = "Turşulu";
            tumNotlar.push(label); 
        } 
    });'''

text = text.replace(old_draft, new_draft)

# Handle Mutually Exclusive Selections in renderChipGroup
old_mutually_exclusive = '''        chip.onclick = () => {
            stateObj[key] = !stateObj[key];
            chip.classList.toggle('selected');
            if (onUpdate) onUpdate();
        };'''

new_mutually_exclusive = '''        chip.onclick = () => {
            stateObj[key] = !stateObj[key];
            chip.classList.toggle('selected');
            
            // Mutually exclusive logic for icerikCikar and icerikEkle
            if (containerId === 'icerikCikarContainer' && stateObj[key]) {
                if (seciliEklenecekler[key]) {
                    seciliEklenecekler[key] = false;
                    renderChipGroup('icerikEkleContainer', malzemeler_listesi, seciliEklenecekler, false, 'chip-yellow');
                }
            } else if (containerId === 'icerikEkleContainer' && stateObj[key]) {
                if (seciliNotlar[key]) {
                    seciliNotlar[key] = false;
                    renderChipGroup('icerikCikarContainer', malzemeler_listesi, seciliNotlar, true, 'chip-red');
                }
            }
            
            if (onUpdate) onUpdate();
        };'''

text = text.replace(old_mutually_exclusive, new_mutually_exclusive)

with codecs.open(app_js, 'w', 'utf-8') as f:
    f.write(text)

print("Updated app.js with İçerik Ekle logic and mutual exclusivity")
