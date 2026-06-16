const colors = ["#F44336", "#9C27B0", "#2196F3", "#4CAF50", "#FFC107", "#FF9800", "#795548", "#FFFFFF"];
const malzemeler_listesi = ["Soğan", "Domates", "Patates", "Ketçap", "Mayonez", "Turşu"];
const ucretsiz_ekstra_listesi = ["Sade Et", "Soslu", "Gemi", "Kayık"];
const odeme_listesi = ["POS", "NAKİT", "Paket", "Dükkan içi"];

let currentColor = localStorage.getItem('waiterColor') || "";
let menuData = { et: [], tavuk: [], kampanya: [], icecekler: [], ekstralar: {} };
let activeTables = [];
let taslakKalemler = [];
let aktifMasaAdi = null;
let siparisEkraniAcik = false;
let ws = null;

// Elements
const topAppBar = document.getElementById('topAppBar');
const appTitle = document.getElementById('appTitle');
const kasaStatus = document.getElementById('kasaStatus');
const backBtn = document.getElementById('backBtn');
const tabRow = document.getElementById('tabRow');
const menuArea = document.getElementById('menuArea');
const masalarArea = document.getElementById('masalarArea');
const masalarList = document.getElementById('masalarList');
const fabMasalar = document.getElementById('fabMasalar');
const bottomAppBar = document.getElementById('bottomAppBar');
const babTitle = document.getElementById('babTitle');
const babSubtitle = document.getElementById('babSubtitle');
const productSheet = document.getElementById('productSheet');
const sheetOverlay = document.getElementById('sheetOverlay');

let currentProduct = null;
let currentQty = 1;
let currentOption = null;
let currentDrinks = {};

// State for chips
let seciliNotlar = {};
let seciliUcretliEkstralar = {};
let seciliUcretsizEkstralar = {};
let seciliOdemeler = {};

function init() {
    initColorSettings();
    fetchMenu();
    connectWebSocket();
    
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const target = e.currentTarget;
            document.querySelector('.tab-btn.active').classList.remove('active');
            target.classList.add('active');
            renderMenu(target.dataset.tab);
        });
    });

    fabMasalar.onclick = () => openMasalarScreen();
    backBtn.onclick = () => closeMasalarScreen();
    document.getElementById('babCancel').onclick = cancelActiveOrder;
    document.getElementById('babSend').onclick = sendOrder;
    
    document.getElementById('qtyMinus').onclick = () => { if (currentQty > 1) { currentQty--; updateSheetPrice(); } };
    document.getElementById('qtyPlus').onclick = () => { currentQty++; updateSheetPrice(); };
    sheetOverlay.onclick = closeProductSheet;
    document.getElementById('addToCartBtn').onclick = addProductToDraft;
}

function initColorSettings() {
    const grid = document.getElementById('colorGrid');
    colors.forEach(c => {
        const circle = document.createElement('div');
        circle.className = 'color-circle' + (c === currentColor ? ' selected' : '');
        circle.style.background = c;
        circle.onclick = () => {
            document.querySelectorAll('.color-circle').forEach(el => el.classList.remove('selected'));
            circle.classList.add('selected');
            currentColor = c;
            localStorage.setItem('waiterColor', c);
        };
        grid.appendChild(circle);
    });

    document.getElementById('settingsBtn').onclick = () => {
        document.getElementById('settingsModal').classList.add('open');
        document.getElementById('settingsOverlay').classList.add('open');
    };
    document.getElementById('closeSettingsBtn').onclick = () => {
        document.getElementById('settingsModal').classList.remove('open');
        document.getElementById('settingsOverlay').classList.remove('open');
    };
}

async function fetchMenu() {
    try {
        const res = await fetch('/menu');
        menuData = await res.json();
        renderMenu('et');
    } catch (e) {
        console.error("Menu fetch error", e);
    }
}

function connectWebSocket() {
    ws = new WebSocket('ws://' + location.host + '/ws');
    ws.onopen = () => { kasaStatus.innerText = "🟢 Kasa Bağlı"; kasaStatus.classList.add('online'); };
    ws.onmessage = (e) => {
        activeTables = JSON.parse(e.data);
        fabMasalar.innerText = `Masalar (${activeTables.length})`;
        if (siparisEkraniAcik) renderMasalarList();
    };
    ws.onclose = () => { kasaStatus.innerText = "🔴 Kasa Çevrimdışı"; kasaStatus.classList.remove('online'); setTimeout(connectWebSocket, 3000); };
    ws.onerror = () => ws.close();
}

function getCardColorClass(name) {
    name = name.toLowerCase();
    if (name.includes("et porsiyon") || name.includes("beyti") || name.includes("iskender")) return "dark-red";
    if (name.includes("hatay usulu")) return "cream";
    if (name.includes("biga doner")) return "blue";
    if (name.includes("tavuk porsiyon") || name.includes("pilav ustu")) return "dark-orange";
    if (name.includes("tombik")) return "orange";
    if (name.includes("eski usul")) return "red";
    if (name.includes("durum")) return "yellow";
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
}

function renderMenu(tab) {
    menuArea.innerHTML = '';
    const items = menuData[tab] || [];
    items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'card ' + getCardColorClass(item.ad);
        card.innerHTML = `
            <div class="card-title">${item.ad}</div>
            <div class="card-price">${item.secenekler[0].fiyat} ₺</div>
        `;
        card.onclick = () => openProductSheet(item, tab === 'icecekler');
        menuArea.appendChild(card);
    });
}

function renderChipGroup(containerId, items, stateObj, isNegative, colorClass, onUpdate) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    items.forEach(item => {
        let label = typeof item === 'string' ? item : item.label;
        let key = typeof item === 'string' ? item : item.key;
        if (isNegative) {
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
        }
        
        const chip = document.createElement('div');
        chip.className = 'chip ' + colorClass;
        chip.innerText = label;
        chip.onclick = () => {
            stateObj[key] = !stateObj[key];
            if (stateObj[key]) chip.classList.add('selected');
            else chip.classList.remove('selected');
            if (onUpdate) onUpdate();
        };
        container.appendChild(chip);
    });
}

function openProductSheet(item, isDrink) {
    currentProduct = item;
    currentQty = 1;
    currentOption = item.secenekler[0];
    currentDrinks = {};
    seciliNotlar = {};
    seciliUcretliEkstralar = {};
    seciliUcretsizEkstralar = {};
    seciliOdemeler = {};

    document.getElementById('sheetProductName').innerText = item.ad;
    document.getElementById('qtyText').innerText = currentQty;
    
    const optsContainer = document.getElementById('optionsContainer');
    optsContainer.innerHTML = '';
    item.secenekler.forEach(sec => {
        const chip = document.createElement('div');
        chip.className = 'chip' + (sec === currentOption ? ' selected' : '');
        let gramajAdi = sec.gr || sec.gramaj;
        chip.innerText = gramajAdi === 'Standart' ? `${sec.fiyat} ₺` : `${gramajAdi} (${sec.fiyat}₺)`;
        chip.onclick = () => {
            currentOption = sec;
            Array.from(optsContainer.children).forEach(c => c.classList.remove('selected'));
            chip.classList.add('selected');
            updateSheetPrice();
        };
        optsContainer.appendChild(chip);
    });

    const icerikCikarSec = document.getElementById('icerikCikarSection');
    const drinksSec = document.getElementById('drinksSection');

    if (!isDrink) {
        icerikCikarSec.classList.remove('hidden');
        renderChipGroup('icerikCikarContainer', malzemeler_listesi, seciliNotlar, true, 'chip-red');
        
        const ucretliArr = Object.keys(menuData.ekstralar || {}).map(k => ({key: k, label: `${k} (+${menuData.ekstralar[k]}₺)`}));
        renderChipGroup('ucretliEkstralarContainer', ucretliArr, seciliUcretliEkstralar, false, 'chip-yellow', updateSheetPrice);
        
        renderChipGroup('ucretsizEkstralarContainer', ucretsiz_ekstra_listesi, seciliUcretsizEkstralar, false, 'chip-dark');
        renderChipGroup('odemeContainer', odeme_listesi, seciliOdemeler, false, 'chip-dark');

        if (menuData['icecekler'] && menuData['icecekler'].length > 0) {
            drinksSec.classList.remove('hidden');
            const dCont = document.getElementById('drinksContainer');
            dCont.innerHTML = '';
            menuData['icecekler'].forEach(ic => {
                const dBtn = document.createElement('button');
                dBtn.className = 'drink-btn ' + getDrinkColorClass(ic.ad);
                dBtn.innerText = ic.ad;
                dBtn.onclick = () => {
                    currentDrinks[ic.ad] = (currentDrinks[ic.ad] || 0) + 1;
                    renderDrinksList(dCont);
                    updateSheetPrice();
                };
                dCont.appendChild(dBtn);
            });
        } else {
            drinksSec.classList.add('hidden');
        }
    } else {
        icerikCikarSec.classList.add('hidden');
        drinksSec.classList.add('hidden');
    }

    document.getElementById('noteInput').value = '';
    
    const masaSec = document.getElementById('masaAdiSection');
    if (aktifMasaAdi) {
        masaSec.classList.add('hidden');
    } else {
        masaSec.classList.remove('hidden');
        document.getElementById('masaInput').value = '';
    }

    updateSheetPrice();
    productSheet.classList.add('open');
    sheetOverlay.classList.add('open');
}

function renderDrinksList(container) {
    Array.from(container.children).forEach(btn => {
        const name = btn.innerText.replace(/[0-9]/g, '').trim();
        const count = currentDrinks[name] || 0;
        if (count > 0) {
            btn.classList.add('selected');
            btn.innerHTML = `${name}<div class="drink-badge">${count}</div>`;
        } else {
            btn.classList.remove('selected');
            btn.innerText = name;
        }
    });
}

function updateSheetPrice() {
    let ucretliFiyat = 0;
    Object.keys(seciliUcretliEkstralar).forEach(k => {
        if (seciliUcretliEkstralar[k]) ucretliFiyat += (menuData.ekstralar[k] || 0);
    });

    let basePrice = (currentOption.fiyat + ucretliFiyat) * currentQty;
    let drinkPrice = 0;
    
    if (menuData['icecekler']) {
        menuData['icecekler'].forEach(ic => {
            if (currentDrinks[ic.ad]) {
                drinkPrice += (currentDrinks[ic.ad] * ic.secenekler[0].fiyat);
            }
        });
    }
    
    const total = basePrice + drinkPrice;
    document.getElementById('addToCartBtn').innerText = `Siparişe Ekle (${total} ₺)`;
}

function closeProductSheet() {
    productSheet.classList.remove('open');
    sheetOverlay.classList.remove('open');
}

function addProductToDraft() {
    const siparisNotu = document.getElementById('noteInput').value.trim();
    let tableInput = document.getElementById('masaInput').value.trim();
    
    if (!aktifMasaAdi) {
        if (!tableInput) tableInput = "Sıra No: " + Math.floor(Math.random() * 1000);
        aktifMasaAdi = tableInput;
        enterActiveTableMode();
    }

    const tumNotlar = [];
    Object.keys(seciliNotlar).forEach(k => { 
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
    Object.keys(seciliUcretsizEkstralar).forEach(k => { if(seciliUcretsizEkstralar[k]) tumNotlar.push(k); });
    Object.keys(seciliUcretliEkstralar).forEach(k => { if(seciliUcretliEkstralar[k]) tumNotlar.push(k); });
    Object.keys(seciliOdemeler).forEach(k => { if(seciliOdemeler[k]) tumNotlar.push(k); });
    if (siparisNotu) tumNotlar.push(siparisNotu);
    
    const birlesikNot = tumNotlar.join(", ");
    
    let ucretliFiyat = 0;
    Object.keys(seciliUcretliEkstralar).forEach(k => {
        if (seciliUcretliEkstralar[k]) ucretliFiyat += (menuData.ekstralar[k] || 0);
    });

    let anlikBirimFiyat = currentOption.fiyat + ucretliFiyat;
    let gramajAdi = currentOption.gr || currentOption.gramaj;

    for (let i = 0; i < currentQty; i++) {
        taslakKalemler.push({ 
            ad: currentProduct.ad, 
            gramaj: gramajAdi, 
            fiyat: anlikBirimFiyat, 
            notlar: birlesikNot 
        });
    }

    if (menuData['icecekler']) {
        menuData['icecekler'].forEach(ic => {
            if (currentDrinks[ic.ad]) {
                let icGramaj = ic.secenekler[0].gr || ic.secenekler[0].gramaj;
                for(let i = 0; i < currentDrinks[ic.ad]; i++){
                    taslakKalemler.push({ 
                        ad: ic.ad, 
                        gramaj: icGramaj, 
                        fiyat: ic.secenekler[0].fiyat, 
                        notlar: "" 
                    });
                }
            }
        });
    }

    updateBottomAppBar();
    closeProductSheet();
}

function enterActiveTableMode() {
    topAppBar.classList.add('active-mode');
    appTitle.innerText = `${aktifMasaAdi} İlave`;
    fabMasalar.classList.add('hidden');
    bottomAppBar.classList.remove('hidden');
}

function cancelActiveOrder() {
    aktifMasaAdi = null;
    taslakKalemler = [];
    topAppBar.classList.remove('active-mode');
    appTitle.innerText = "SARAÇOĞLU DÖNER";
    fabMasalar.classList.remove('hidden');
    bottomAppBar.classList.add('hidden');
}

function updateBottomAppBar() {
    babTitle.innerText = `Masa: ${aktifMasaAdi}`;
    const total = taslakKalemler.reduce((sum, i) => sum + i.fiyat, 0);
    babSubtitle.innerText = `${taslakKalemler.length} Ürün - ${total} ₺`;
}

function openMasalarScreen() {
    siparisEkraniAcik = true;
    appTitle.innerText = "Açık Masalar";
    kasaStatus.classList.add('hidden');
    document.getElementById('settingsBtn').classList.add('hidden');
    backBtn.classList.remove('hidden');
    tabRow.classList.add('hidden');
    menuArea.classList.add('hidden');
    fabMasalar.classList.add('hidden');
    masalarArea.classList.remove('hidden');
    renderMasalarList();
}

function closeMasalarScreen() {
    siparisEkraniAcik = false;
    appTitle.innerText = "SARAÇOĞLU DÖNER";
    kasaStatus.classList.remove('hidden');
    document.getElementById('settingsBtn').classList.remove('hidden');
    backBtn.classList.add('hidden');
    tabRow.classList.remove('hidden');
    menuArea.classList.remove('hidden');
    if (!aktifMasaAdi) fabMasalar.classList.remove('hidden');
    masalarArea.classList.add('hidden');
}

window.deleteItem = function(musteri_adi, index) {
    if(!confirm('Bu ürünü silmek istediğinize emin misiniz?')) return;
    const table = activeTables.find(t => t.musteri_adi === musteri_adi);
    if (!table) return;
    table.kalemler.splice(index, 1);
    
    if (table.kalemler.length === 0) {
        fetch('/hesap_kapat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ musteri_adi: musteri_adi }) });
    } else {
        const total = table.kalemler.reduce((sum, i) => sum + i.fiyat, 0);
        const data = { musteri_adi: musteri_adi, kalemler: table.kalemler, toplam_tutar: total, renk: table.renk };
        fetch('/siparis', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    }
};

window.editNote = function(musteri_adi, index) {
    const table = activeTables.find(t => t.musteri_adi === musteri_adi);
    if (!table) return;
    const currentNote = table.kalemler[index].notlar || "";
    const newNote = prompt("Yeni notu girin:", currentNote);
    if (newNote !== null) {
        table.kalemler[index].notlar = newNote.trim();
        const total = table.kalemler.reduce((sum, i) => sum + i.fiyat, 0);
        const data = { musteri_adi: musteri_adi, kalemler: table.kalemler, toplam_tutar: total, renk: table.renk };
        fetch('/siparis', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    }
};

function renderMasalarList() {
    masalarList.innerHTML = '';
    activeTables.forEach(t => {
        const card = document.createElement('div');
        card.className = 'adisyon-card';
        let itemsHtml = t.kalemler.map((k, index) => `
            <div style="border-bottom: 1px solid #444; padding: 10px 0;">
                <div class="a-item" style="display:flex; justify-content:space-between; align-items:center;">
                    <div class="a-item-name" style="flex:1;">1x ${k.ad} ${k.gramaj!=='Standart' ? `(${k.gramaj})` : ''}</div>
                    <div style="display:flex; align-items:center; gap: 8px;">
                        <div class="a-item-price" style="margin-right: 8px;">${k.fiyat} ₺</div>
                        <button class="btn-icon-small" onclick="editNote('${t.musteri_adi}', ${index})">✏️</button>
                        <button class="btn-icon-small" onclick="deleteItem('${t.musteri_adi}', ${index})" style="color:var(--danger);">🗑️</button>
                    </div>
                </div>
                ${k.notlar ? `<div style="font-size:12px; color:#aaa; margin-top:4px;">* ${k.notlar}</div>` : ''}
            </div>
        `).join('');
        
        let colorIndicator = t.renk ? `<div style="width:16px; height:16px; border-radius:50%; background-color:${t.renk}; margin-right:8px; display:inline-block; vertical-align:middle;"></div>` : '';
        card.innerHTML = `
            <div class="adisyon-header" style="display:flex; align-items:center; justify-content:space-between;">
                <div class="adisyon-title" style="display:flex; align-items:center;">
                    ${colorIndicator}
                    ${t.musteri_adi}
                </div>
                <div class="adisyon-time">${t.saat || ''}</div>
            </div>
            <div class="adisyon-items">${itemsHtml}</div>
            <div class="adisyon-footer" style="flex-direction: column; gap: 12px; margin-top: 8px;">
                <div style="display:flex; justify-content:space-between; width:100%;">
                    <div class="adisyon-total" style="font-size:24px;">TOPLAM: ${t.toplam_tutar} ₺</div>
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; width:100%;">
                    <button class="btn-ilave" style="background:#2196F3;">➕ İlave</button>
                    <button class="btn-yazdir" style="background:#424242;">🖨️ Fiş Yazdır</button>
                    <button class="btn-tamam" style="background:#4CAF50; grid-column: span 2;">✅ Ödendi / Kapat</button>
                </div>
            </div>
        `;
        
        card.querySelector('.btn-ilave').onclick = () => {
            aktifMasaAdi = t.musteri_adi;
            taslakKalemler = [...t.kalemler];
            closeMasalarScreen();
            enterActiveTableMode();
            updateBottomAppBar();
        };
        card.querySelector('.btn-tamam').onclick = () => {
            fetch('/hesap_kapat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ musteri_adi: t.musteri_adi }) });
        };
        card.querySelector('.btn-yazdir').onclick = () => {
            fetch('/yazdir', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ musteri_adi: t.musteri_adi }) });
        };
        masalarList.appendChild(card);
    });
}

async function sendOrder() {
    if (taslakKalemler.length === 0) return;
    const total = taslakKalemler.reduce((sum, i) => sum + i.fiyat, 0);
    const m_adi = aktifMasaAdi;
    const data = {
        musteri_adi: m_adi.startsWith("Sıra No:") ? "" : m_adi,
        kalemler: taslakKalemler,
        toplam_tutar: total,
        renk: currentColor
    };
    try {
        const req = await fetch('/siparis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (req.ok) cancelActiveOrder();
        else alert("Gönderilemedi! Kasa uygulamasında hata olabilir.");
    } catch (e) {
        alert("Kasa bağlantı hatası!");
    }
}

init();
