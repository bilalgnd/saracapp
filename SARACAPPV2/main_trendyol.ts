import axios from 'axios'
import * as fs from 'fs'
import { join } from 'path'
import { app } from 'electron'
import { activeOrders, saveOrders, getNextQueueNo } from './models'
import { broadcastUpdateToPhones, notifyUI } from './server'

const TRENDYOL_SUPPLIER_ID = '6647850'
const TRENDYOL_API_KEY = 'bYv2F8LWu5QAHfucbind'
const TRENDYOL_API_SECRET = 'zCFUGzkEL4kjXkdZ9ZRN'

// Basic Auth token oluşturma
const authToken = Buffer.from(`${TRENDYOL_API_KEY}:${TRENDYOL_API_SECRET}`).toString('base64')

// İşlenmiş siparişlerin ID'lerini tutalım (tekrar aynı siparişi eklememek için)
const processedPackageIds = new Set<string>()

// Müşteri sipariş sayılarını kalıcı tutmak için
let customerOrdersCount: Record<string, number> = {}
let customersFile = 'trendyol_customers.json'

export function startTrendyolPolling() {
  const userDataPath = app.getPath('userData')
  customersFile = join(userDataPath, 'trendyol_customers.json')
  
  if (fs.existsSync(customersFile)) {
    try {
      customerOrdersCount = JSON.parse(fs.readFileSync(customersFile, 'utf-8'))
    } catch (e) {}
  }

  setInterval(async () => {
    try {
      const url = `https://api.tgoapis.com/integrator/order/meal/suppliers/${TRENDYOL_SUPPLIER_ID}/packages`
      
      const response = await axios.get(url, {
        headers: {
          'Authorization': `Basic ${authToken}`,
          'User-Agent': `${TRENDYOL_SUPPLIER_ID} - SelfIntegration`,
          'x-agentname': 'saracoglu-pos',
          'x-executor-user': 'info@saracoglu.com'
        }
      })

      // Yanıt genellikle { content: [ ...paketler ] } şeklinde gelir.
      // Eğer Trendyol API dökümanı güncellendiyse (örneğin sadece [] dönüyorsa), buna göre adapte oluyoruz.
      let packages: any[] = []
      if (response.data && Array.isArray(response.data.content)) {
        packages = response.data.content
      } else if (Array.isArray(response.data)) {
        packages = response.data
      }

      if (packages.length > 0) {
        let hasNewOrder = false

        for (const pkg of packages) {
          // Sadece 'Created' durumundaki yeni siparişleri işleyelim
          if (pkg.packageStatus !== 'Created') continue

          const pkgId = pkg.packageId || pkg.id || pkg.orderNumber

          if (!pkgId || processedPackageIds.has(pkgId.toString())) {
            continue
          }

          // Müşteri bilgileri ve sipariş sayısını takip etme
          const firstName = pkg.customer?.firstName || 'Müşteri'
          const lastName = pkg.customer?.lastName || ''
          const customerKey = `${firstName}_${lastName}`.trim()
          
          customerOrdersCount[customerKey] = (customerOrdersCount[customerKey] || 0) + 1
          const orderCount = customerOrdersCount[customerKey]
          fs.writeFileSync(customersFile, JSON.stringify(customerOrdersCount))

          // Adres özeti (Mahalle vb.)
          const neighborhood = pkg.address?.neighborhood || pkg.address?.district || 'Bilinmeyen Adres'
          
          let customerName = `TY - ${neighborhood}`
          if (orderCount > 1) {
            customerName += ` (${orderCount}. Sipariş)`
          }

          let customerNote = pkg.customerNote || '' // Trendyol'da not bazen genel objede, bazen adreste olur
          customerNote = customerNote.replace(/-?\s*\**\s*ÇATAL[- ]BIÇAK GÖNDERMEYİN/gi, '').trim()
          let addressDesc = pkg.address?.addressDescription || pkg.address?.address1 || ''
          addressDesc = addressDesc.replace(/\d{5}\s*[a-zA-ZçğıöşüÇĞİÖŞÜ]+\s*/g, '').replace(/biga/gi, '').replace(/çanakkale/gi, '').replace(/,\s*/g, ' ').replace(/\s+/g, ' ').trim()
          
          let paymentStr = 'Online'
          if (typeof pkg.paymentMethod === 'string') paymentStr = pkg.paymentMethod
          else if (pkg.paymentMethod?.name) paymentStr = pkg.paymentMethod.name
          else if (pkg.paymentMethodText) paymentStr = pkg.paymentMethodText
          
          const orderNote = [
            `Ödeme: ${paymentStr}`,
            `${firstName} ${lastName}`,
            customerNote ? `Not: ${customerNote}` : '',
            addressDesc ? `📍 ${addressDesc}` : ''
          ].filter(Boolean).join('\n')
          
          let items: any[] = []
          let totalAmount = pkg.totalPrice || 0

          if (pkg.lines && Array.isArray(pkg.lines)) {
            pkg.lines.forEach((line: any) => {
              const modifierNotes = (line.merchantOptionModifiers || []).map((m: any) => m.name).filter((name: string) => !name.toLowerCase().includes('standart')).join(' | ')
              const qty = line.quantity || 1
              const unitPrice = (line.price || 0) / qty
              for (let i = 0; i < qty; i++) {
                items.push({
                  name: line.name || line.productName || 'Ürün',
                  portion: '',
                  price: unitPrice,
                  notes: modifierNotes
                })
              }
            })
          }

          const newOrder = {
            customer_name: customerName,
            masa_no: getNextQueueNo().toString(),
            order_note: orderNote,
            order_id: pkgId.toString(),
            time: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }),
            items: items,
            total_amount: totalAmount,
            status: 'waiting',
            color: '#FF9800' // Trendyol Turuncusu
          }

          activeOrders.unshift(newOrder)
          processedPackageIds.add(pkgId.toString())
          hasNewOrder = true
          
          notifyUI('order_received', newOrder)
        }

        if (hasNewOrder) {
          saveOrders()
          broadcastUpdateToPhones()
        }
      }

    } catch (error: any) {
      if (error.response) {
        console.error('Trendyol API Hatası:', error.response.status, error.response.data)
      } else {
        console.error('Trendyol Bağlantı Hatası:', error.message)
      }
    }
  }, 20000) // Her 20 saniyede bir
}
