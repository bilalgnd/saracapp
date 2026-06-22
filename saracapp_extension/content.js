console.log("SaraçApp Entegrasyon Uzantısı Yüklendi!");

function addBadge(platform) {
    const badge = document.createElement("div");
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
    btn.innerText = "KODLARI GÖNDER";
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
            setTimeout(() => btn.innerText = "KODLARI GÖNDER", 3000);
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

    // Hide by default
    badge.style.display = "none";
    document.body.appendChild(badge);

    // Hotkey to toggle badge (Ctrl + Q)
    document.addEventListener("keydown", (e) => {
        if (e.ctrlKey && (e.key === "q" || e.key === "Q")) {
            badge.style.display = badge.style.display === "none" ? "block" : "none";
        }
    });
}

function sendOrderToBackend(orderData) {
    fetch("http://localhost:5000/siparis", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(orderData)
    })
    .then(res => res.json())
    .catch(err => console.error("Backend bağlantı hatası: ", err));
}

let currentPlatform = "";
if (window.location.hostname.includes("trendyol") || window.location.hostname.includes("tgoyemek")) {
    currentPlatform = "Trendyol";
} else if (window.location.hostname.includes("yemeksepeti")) {
    currentPlatform = "Yemeksepeti";
}

if (currentPlatform) {
    setTimeout(() => {
        addBadge(currentPlatform);
        
        const observer = new MutationObserver((mutations) => {
            // Otomatik veri çekme işlemleri buraya eklenecek
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }, 2000);
}
