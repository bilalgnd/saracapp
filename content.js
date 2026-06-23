console.log("SaraçApp Entegrasyon Uzantısı Yüklendi!");

let processedOrderIds = new Set();

function addBadge(platform) {
    const badge = document.createElement("div");
    badge.id = "saracapp-badge";
    badge.style.position = "fixed";
    badge.style.bottom = "20px";
    badge.style.right = "20px";
    badge.style.backgroundColor = platform === 'Trendyol' ? '#FF9800' : '#E91E63';
    badge.style.color = "white";
    badge.style.padding = "10px 20px";
    badge.style.borderRadius = "8px";
    badge.style.fontFamily = "sans-serif";
    badge.style.fontWeight = "bold";
    badge.style.zIndex = "999999";
    badge.style.boxShadow = "0 4px 6px rgba(0,0,0,0.3)";
    
    badge.innerHTML = `SARAÇAPP AKTİF (${platform})<br><br>`;
    
    // Debug Button
    const btn = document.createElement("button");
    btn.innerText = "KODLARI GÖNDER (DEBUG)";
    btn.style.padding = "5px 10px";
    btn.style.cursor = "pointer";
    btn.style.color = "black";
    btn.onclick = () => {
        btn.innerText = "Gönderiliyor...";
        fetch("http://localhost:5000/debug_html", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                platform: platform,
                html: document.body.innerHTML
            })
        }).then(() => {
            btn.innerText = "BAŞARILI!";
            setTimeout(() => btn.innerText = "KODLARI GÖNDER (DEBUG)", 3000);
        }).catch(() => {
            btn.innerText = "HATA!";
        });
    };
    badge.appendChild(btn);

    // Hide Button
    const hideBtn = document.createElement("button");
    hideBtn.innerText = "Gizle";
    hideBtn.style.padding = "5px 10px";
    hideBtn.style.marginLeft = "10px";
    hideBtn.style.cursor = "pointer";
    hideBtn.style.color = "black";
    hideBtn.style.backgroundColor = "#ccc";
    hideBtn.style.border = "none";
    hideBtn.style.borderRadius = "4px";
    hideBtn.onclick = () => {
        badge.style.display = "none";
    };
    badge.appendChild(hideBtn);

    document.body.appendChild(badge);

    // Hotkey to toggle badge (Ctrl + Q)
    document.addEventListener("keydown", (e) => {
        if (e.ctrlKey && (e.key === "q" || e.key === "Q")) {
            badge.style.display = badge.style.display === "none" ? "block" : "none";
        }
    });
}

function sendOrderToBackend(orderData) {
    console.log("SaraçApp'e Gönderilen Sipariş:", orderData);
    fetch("http://localhost:5000/siparis", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(orderData)
    })
    .then(res => res.json())
    .catch(err => console.error("Backend bağlantı hatası: ", err));
}

// ==========================================
// TRENDYOL PARSER
// ==========================================
function parseTrendyol() {
    // Trendyol detay sayfası veya popover açık mı diye kontrol et
    const detailPanel = document.querySelector('.order-details') || document.querySelector('.order-card__popover__content');
    if (!detailPanel) return;

    let orderCodeEl = document.querySelector('.order-details-header__order-code') || document.querySelector('.order-card__popover__title__main');
    if (!orderCodeEl) return;
    
    let orderId = orderCodeEl.innerText.trim();
    if (processedOrderIds.has(orderId)) return; // Daha önce gönderildiyse es geç

    let customerNameEl = document.querySelector('.order-details-info__item__content'); // Detay sayfası için müşteri adı
    let customerName = customerNameEl ? customerNameEl.innerText.trim() : "Trendyol Müşterisi";

    let items = [];
    
    // Yöntem 1: Detay sayfasındaki ürün listesi (.order-item--product)
    let productRows = document.querySelectorAll('.order-item--product');
    if (productRows.length > 0) {
        productRows.forEach(row => {
            let nameEl = row.querySelector('.order-item--product__name');
            let countEl = row.querySelector('.order-item__count');
            if (nameEl && countEl) {
                items.push({
                    name: nameEl.innerText.trim(),
                    quantity: countEl.innerText.trim().replace(/[^0-9]/g, '') || "1"
                });
            }
        });
    } else {
        // Yöntem 2: Popover (Küçük önizleme kutusu) içindeki items
        let popoverItems = document.querySelectorAll('.order-card__popover__items__item');
        popoverItems.forEach(item => {
            let text = item.innerText.trim(); // Örn: "3 Adet Tavuk Döner Dürüm"
            let match = text.match(/^(\d+)\s*Adet\s*(.+)$/i);
            if (match) {
                items.push({ quantity: match[1], name: match[2].trim() });
            } else {
                items.push({ quantity: "1", name: text });
            }
        });
    }

    if (items.length > 0) {
        processedOrderIds.add(orderId);
        sendOrderToBackend({
            platform: "Trendyol",
            order_id: orderId,
            customer_name: customerName,
            items: items
        });
    }
}

// ==========================================
// YEMEKSEPETI PARSER
// ==========================================
function parseYemeksepeti() {
    let items = [];
    
    // Müşteri Notları ve Ürünleri sırayla taramak için <hr> sonrasına bakıyoruz
    let hrElements = document.querySelectorAll('hr');
    if (hrElements.length === 0) return;
    
    let hr = hrElements[hrElements.length - 1]; // Sipariş detaylarını ayıran çizgi
    let orderContainer = hr.nextElementSibling;
    if (!orderContainer) return;

    let nodes = orderContainer.querySelectorAll('h5, p');
    let currentItem = null;

    nodes.forEach(node => {
        let text = node.innerText.trim();
        if (!text) return;
        
        let tagName = node.tagName.toLowerCase();
        
        // Yeni bir Ana Ürün başlangıcı (Örn: "2 x")
        if (tagName === 'h5' && text.match(/^\d+\s*x$/)) {
            let quantity = text.replace('x', '').trim();
            let parentContainer = node.parentElement;
            let productName = "Bilinmeyen Ürün";
            if (parentContainer && parentContainer.nextElementSibling) {
                productName = parentContainer.nextElementSibling.innerText.trim();
            }
            
            currentItem = {
                name: productName,
                quantity: quantity,
                notes: ""
            };
            items.push(currentItem);
        }
        else if (currentItem) {
            // Alt ürün / Özellik mi? (Örn: "100Gr", "Ayran")
            if (tagName === 'p' && node.getAttribute('aria-label') === 'item-name') {
                currentItem.name += "\n(-> " + text + ")";
            }
            // Müşteri notu mu?
            else if (tagName === 'p' && node.className.includes('caption-500')) {
                // "ÇATAL-BIÇAK GÖNDERMEYİN" sistem notunu yoksay
                if (!text.toUpperCase().includes("ÇATAL") && !text.toUpperCase().includes("BIÇAK")) {
                    currentItem.notes += (currentItem.notes ? "\n" : "") + "NOT: " + text;
                }
            }
        }
    });
    if (items.length > 0) {
        // Müşteri adını bulmak için (Genellikle adresin hemen üstündedir, order card içinde ŞEYDA ŞAHİN yazar)
        // Eğer bulamazsak varsayılan bir isim atayalım. Sipariş kodunu bulmaya çalışalım.
        let orderIdEl = document.querySelector('h4') || document.querySelector('[data-testid="accepted-order-list-item"] h6');
        let orderId = orderIdEl ? orderIdEl.innerText.trim() : "YS-" + Date.now();
        
        // Sipariş mükerrer gönderilmesin
        let uniqueKey = items.map(i => i.name).join("-");
        if (processedOrderIds.has(uniqueKey)) return;
        
        processedOrderIds.add(uniqueKey);
        
        sendOrderToBackend({
            platform: "Yemeksepeti",
            order_id: orderId,
            customer_name: "Yemeksepeti Müşterisi", // Şimdilik varsayılan, API veya DOM'dan çekilebilir.
            items: items
        });
    }
}

// ==========================================
// MAIN OBSERVER
// ==========================================
let currentPlatform = "";
if (window.location.hostname.includes("trendyol") || window.location.hostname.includes("tgoyemek")) {
    currentPlatform = "Trendyol";
} else if (window.location.hostname.includes("yemeksepeti")) {
    currentPlatform = "Yemeksepeti";
}

if (currentPlatform) {
    // UI Yüklendiğinde butonu ekle
    setTimeout(() => {
        addBadge(currentPlatform);
        
        console.log(`SaraçApp dinlemeye başladı: ${currentPlatform}`);
        
        // Sayfadaki DOM değişikliklerini dinle
        const observer = new MutationObserver((mutations) => {
            if (currentPlatform === "Trendyol") {
                parseTrendyol();
            } else if (currentPlatform === "Yemeksepeti") {
                parseYemeksepeti();
            }
        });
        
        observer.observe(document.body, { childList: true, subtree: true });
        
        // Sayfa yüklendiğinde mevcut açık sipariş varsa kontrol et
        if (currentPlatform === "Trendyol") parseTrendyol();
        if (currentPlatform === "Yemeksepeti") parseYemeksepeti();
        
    }, 2000);
}
