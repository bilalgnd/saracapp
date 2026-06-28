const API_ENDPOINT = 'http://127.0.0.1:5000/yemeksepeti_siparis';

function extractYemeksepetiOrder() {
    const container = document.querySelector('[data-testid="side-drawer-layout-content"]') || document;

    const orderData = {
        orderId: container.querySelector('[data-testid="new-order-short-code"]')?.textContent.trim(),
        orderHash: container.querySelector('[data-testid="new-order-short-code"]')?.nextElementSibling?.textContent.trim(),
        customerName: null,
        phone: null,
        address: null,
        note: container.querySelector('.muiltr-orders-qke3em')?.textContent.trim() || "",
        paymentMethod: null,
        items: [],
        totalAmount: null
    };

    const allText = container.innerText || "";
    if (allText.match(/nakit/i)) orderData.paymentMethod = "Nakit";
    else if (allText.match(/kredi.*kart/i)) orderData.paymentMethod = "Kredi Kartı";
    else if (allText.match(/online/i)) orderData.paymentMethod = "Online";

    const musteriLabel = Array.from(container.querySelectorAll('p')).find(p => p.textContent.trim() === 'Müşteri');
    if (musteriLabel && musteriLabel.nextElementSibling) {
        orderData.customerName = musteriLabel.nextElementSibling.textContent.trim();
    }

    const phoneIcon = container.querySelector('svg.cape-phone');
    if (phoneIcon && phoneIcon.nextElementSibling) {
        orderData.phone = phoneIcon.nextElementSibling.textContent.trim();
    }

    const locationIcon = container.querySelector('svg.cape-location-on');
    if (locationIcon && locationIcon.nextElementSibling) {
        const addressNodes = locationIcon.nextElementSibling.querySelectorAll('p');
        orderData.address = Array.from(addressNodes).map(p => p.textContent.trim()).join(' | ');
    }

    const itemRows = container.querySelectorAll('.muiltr-orders-18r20nv');
    itemRows.forEach(row => {
        const qty = row.querySelector('.muiltr-orders-10krtj2 span')?.textContent.trim();
        const name = row.querySelector('.muiltr-orders-9qvils span')?.textContent.trim();
        const price = row.querySelector('.muiltr-orders-v4n9ng span[aria-label="currency"]')?.textContent.trim();
        
        const subItems = Array.from(row.querySelectorAll('.muiltr-orders-beomsi .muiltr-orders-9qvils span'))
            .map(el => el.textContent.trim());

        if (name) {
            orderData.items.push({ quantity: qty, name: name, price: price, options: subItems });
        }
    });

    const totalSection = container.querySelector('.muiltr-orders-19toiec');
    if (totalSection) {
        const totalSpans = totalSection.querySelectorAll('span[aria-label="currency"]');
        if (totalSpans.length > 0) {
            orderData.totalAmount = totalSpans[0].textContent.trim();
        }
    }

    return orderData;
}

function initYemeksepetiObserver() {
    const observer = new MutationObserver((mutationsList) => {
        for (const mutation of mutationsList) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                const orderPanel = document.querySelector('[data-testid="side-drawer-layout-content"]');
                
                if (orderPanel && !orderPanel.dataset.scraped) {
                    orderPanel.dataset.scraped = "true";
                    
                    setTimeout(() => {
                        const orderData = extractYemeksepetiOrder();
                        if (orderData.orderId) {
                            sendOrderToAPI(orderData);
                        }
                    }, 500); 
                }
            }
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });
}

function sendOrderToAPI(data) {
    fetch(API_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }).catch(error => console.error('Fetch Hatası:', error));
}

initYemeksepetiObserver();
