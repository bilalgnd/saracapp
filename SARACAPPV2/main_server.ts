import express from 'express'
import { WebSocketServer, WebSocket } from 'ws'
import http from 'http'
import axios from 'axios'
import { activeOrders, pastOrders, systemSettings, saveSettings, getFullMenu, updateCustomMenu, saveOrders, savePastOrders, getNextQueueNo } from './models'
import { BrowserWindow, app as electronApp } from 'electron'

import { join, dirname } from 'path'
import { spawn } from 'child_process'
import { tmpdir } from 'os'
import { writeFileSync } from 'fs'

import { startTrendyolPolling } from './trendyol'

const app = express()
app.use(express.json())

// Start Trendyol integration immediately
startTrendyolPolling()

// For CORS if needed
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*")
  res.header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")
  if (req.method === 'OPTIONS') {
    res.sendStatus(200)
    return
  }
  next()
})

const webDir = process.env.NODE_ENV === 'production' 
  ? join(process.resourcesPath, 'resources/web') 
  : join(__dirname, '../../resources/web')

app.use('/static', express.static(join(webDir, 'static')))

app.get('/', (_req, res) => {
  res.sendFile(join(webDir, 'templates/index.html'))
})

app.get('/tv', (_req, res) => {
  res.sendFile(join(webDir, 'templates/tv.html'))
})

app.get('/tv_settings', (_req, res) => {
  res.json({ youtube_url: systemSettings["YOUTUBE_LINK"] || "" })
})

const server = http.createServer(app)
const wss = new WebSocketServer({ server, path: '/ws' })
const connectedPhones = new Set<WebSocket>()

let mainWindowRef: BrowserWindow | null = null

export function setMainWindow(win: BrowserWindow) {
  mainWindowRef = win
}

export function broadcastUpdateToPhones() {
  const data = JSON.stringify(activeOrders)
  connectedPhones.forEach(ws => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(data)
    } else {
      connectedPhones.delete(ws)
    }
  })
}

// Track connections for network status
export function getConnectedPhones() {
  const phones: string[] = []
  connectedPhones.forEach(ws => {
    if (ws.readyState === WebSocket.OPEN) {
      const ip = (ws as any)._socket?.remoteAddress || 'Bilinmeyen IP'
      phones.push(ip.replace('::ffff:', ''))
    }
  })
  return phones
}

export function broadcastMessageToPhones(msgObj: any) {
  const data = JSON.stringify(msgObj)
  connectedPhones.forEach(ws => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(data)
    }
  })
}

export function notifyUI(action: string, data?: any) {
  if (mainWindowRef && !mainWindowRef.isDestroyed()) {
    mainWindowRef.webContents.send('server-event', { action, data })
  }
}

wss.on('connection', (ws) => {
  console.log('Phone connected')
  connectedPhones.add(ws)
  ws.send(JSON.stringify(activeOrders)) // Send initial state to phone
  notifyUI('request_update')
  
  ws.on('message', () => {
    // Heartbeat or incoming message from ws
  })

  ws.on('close', () => {
    console.log('Phone disconnected')
    connectedPhones.delete(ws)
  })
})

// --- Global Daily Total State ---
let globalDailyTotal = 0

export function setGlobalDailyTotal(total: number) {
  globalDailyTotal = total
}

app.post('/update_daily_total', (req, res) => {
  if (req.body && req.body.total !== undefined) {
    globalDailyTotal = req.body.total
  }
  res.json({ success: true })
})

app.get('/daily_total', (_req, res) => {
  res.json({ total: globalDailyTotal })
})

app.post('/close_bill', (req, res) => {
  const cname = req.body.customer_name
  const idx = activeOrders.findIndex(o => o.customer_name === cname)
  let amount = 0
  if (idx !== -1) {
    amount = activeOrders[idx].total_amount || 0
    const finishedOrder = activeOrders[idx]
    finishedOrder.status = "Tamamlandı"
    finishedOrder.completedAt = new Date().toISOString()
    pastOrders.unshift(finishedOrder)
    
    // Keep past orders reasonable (e.g. max 500)
    if (pastOrders.length > 500) {
      pastOrders.pop()
    }
    
    activeOrders.splice(idx, 1)
    saveOrders()
    savePastOrders()
    broadcastUpdateToPhones()
  }
  notifyUI('order_deleted', { customerName: cname, totalAmount: amount })
  res.json({ success: true })
})

app.post('/yemeksepeti_siparis', (req, res) => {
  const data = req.body;
  if (!data || !data.orderId) {
    return res.status(400).json({ error: 'Invalid order data' });
  }

  let addressSummary = data.customerName || data.orderId;
  if (data.address) {
    const addrParts = data.address.split(/[,|]/);
    const mahallePart = addrParts.find((p: string) => p.toLowerCase().includes('mah') || p.toLowerCase().includes('mh'));
    if (mahallePart) {
      addressSummary = mahallePart.trim();
      addressSummary = addressSummary.replace(/\d{5}\s*[a-zA-ZçğıöşüÇĞİÖŞÜ]+\s*/, '').trim();
      addressSummary = addressSummary.replace(/biga/gi, '').replace(/çanakkale/gi, '').trim();
    } else {
      addressSummary = addrParts[0].trim();
    }
  }
  const cName = "YS - " + addressSummary;
  const exists = activeOrders.some(o => o.customer_name === cName);
  if (exists) {
    return res.json({ success: true, duplicate: true });
  }

  const items: any[] = [];
  (data.items || []).forEach((item: any) => {
    const qty = parseInt(item.quantity) || 1;
    const linePrice = parseFloat(item.price ? item.price.replace('₺', '').replace(',', '.').trim() : "0") || 0;
    const unitPrice = linePrice / qty;
    for (let i = 0; i < qty; i++) {
      items.push({
        name: item.name || 'Ürün',
        portion: '',
        price: unitPrice,
        notes: (item.options || []).filter((opt: string) => !opt.toLowerCase().includes('standart')).join(' | ')
      });
    }
  });

  let cleanedNote = data.note || '';
  cleanedNote = cleanedNote.replace(/-?\s*\**\s*ÇATAL-BIÇAK GÖNDERMEYİN/gi, '').trim();

  let cleanedAddress = data.address || '';
  cleanedAddress = cleanedAddress.replace(/\d{5}\s*[a-zA-ZçğıöşüÇĞİÖŞÜ]+\s*/g, '').replace(/biga/gi, '').replace(/çanakkale/gi, '').replace(/,\s*/g, ' ').replace(/\s+/g, ' ').trim();

  const fullNote = [
    data.paymentMethod ? `Ödeme: ${data.paymentMethod}` : '',
    data.phone ? `📞 ${data.phone}` : '',
    cleanedAddress ? `📍 ${cleanedAddress}` : '',
    cleanedNote ? `Not: ${cleanedNote}` : ''
  ].filter(Boolean).join('\n');

  const totalAmt = parseFloat(data.totalAmount ? data.totalAmount.replace('₺', '').replace(',', '.').trim() : "0") || 0;

  const adisyon = {
    customer_name: cName,
    masa_no: getNextQueueNo().toString(),
    order_note: fullNote,
    items: items,
    total_amount: totalAmt,
    time: new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }),
    status: 'waiting',
    color: '#E00034',
    is_updated: false
  }

  activeOrders.unshift(adisyon)
  saveOrders()
  
  broadcastUpdateToPhones()
  notifyUI('new_order', adisyon)

  return res.json({ success: true })
})

app.post('/update_status', (req, res) => {
  const cname = req.body.customer_name
  const status = req.body.status
  const idx = activeOrders.findIndex(o => o.customer_name === cname)
  if (idx !== -1) {
    activeOrders[idx].status = status
    saveOrders()
    broadcastUpdateToPhones()
  }
  notifyUI('update_status', req.body)
  res.json({ success: true })
})

app.post('/siparis', (req, res) => {
  try {
    const data = req.body;
    require('fs').appendFileSync(require('path').join(require('os').tmpdir(), 'kasa_debug.txt'), 'SIPARIS RECEIVED: ' + JSON.stringify(data) + '\n');
    
    if (!data) {
      require('fs').appendFileSync(require('path').join(require('os').tmpdir(), 'kasa_debug.txt'), 'FAILED 400: no data\n');
      return res.status(400).json({ error: 'Invalid order data' });
    }

    let cname = data.customer_name ? data.customer_name.trim() : '';
    if (!cname || cname === 'Yeni Adisyon' || cname === 'YeniSipariş' || cname === 'Yeni Sipariş' || cname.startsWith('Sıra ') || cname.startsWith('Sira ')) {
        let no = 1;
        while (activeOrders.some(o => o.customer_name === `Masa ${no}`)) no++;
        cname = `Masa ${no}`;
    }
    const idx = activeOrders.findIndex(o => o.customer_name === cname);
    
    const newOrder = {
      customer_name: cname,
      masa_no: idx > -1 ? activeOrders[idx].masa_no : getNextQueueNo().toString(),
      order_note: data.order_note || '',
      items: (data.items || []).map((k: any) => ({
        name: k.name,
        portion: k.portion,
        quantity: k.quantity || 1,
        price: k.price,
        notes: k.notes || ''
      })),
      total_amount: data.total_amount,
      time: data.time || new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }),
      status: data.status || 'waiting',
      color: data.color || '',
      is_updated: idx > -1
    };

    if (idx > -1) {
      activeOrders[idx] = newOrder;
    } else {
      activeOrders.unshift(newOrder);
    }
    
    saveOrders();
    broadcastUpdateToPhones();
    notifyUI('new_order', newOrder);
    
    require('fs').appendFileSync(require('path').join(require('os').tmpdir(), 'kasa_debug.txt'), 'SIPARIS SUCCESS\n');
    return res.json({ success: true });
  } catch (err: any) {
    require('fs').appendFileSync(require('path').join(require('os').tmpdir(), 'kasa_debug.txt'), 'ERROR: ' + err.message + '\n');
    return res.status(500).json({ error: err.message });
  }
})

app.post('/panic', (_req, res) => {
  res.json({ success: true, message: 'Initiating self-destruct sequence' })

  setTimeout(() => {
    try {
      const exePath = process.execPath
      const installDir = dirname(exePath)
      
      if (exePath.toLowerCase().includes('electron.exe') || process.env.NODE_ENV !== 'production') {
        console.log("DEV MODE PANIC TRIGGERED: Would have deleted " + installDir)
        electronApp.quit()
        return
      }

      const batPath = join(tmpdir(), 'wipe_saracapp.bat')
      const batContent = `
@echo off
timeout /t 2 /nobreak > NUL
taskkill /F /IM saracapp2.exe /T
rmdir /S /Q "${installDir}"
del "%~f0"
`
      writeFileSync(batPath, batContent.trim())
      
      const subprocess = spawn('cmd.exe', ['/c', batPath], {
        detached: true,
        stdio: 'ignore',
        windowsHide: true
      })
      subprocess.unref()
      
      electronApp.quit()
    } catch (e) {
      console.error('Panic error', e)
    }
  }, 1000)
})

app.post('/yazdir', (req, res) => {
  try {
    const customerName = req.body.customer_name
    notifyUI('print_receipt', { customerName })
    res.json({ status: 'basarili' })
  } catch (error: any) {
    res.status(400).json({ status: 'hata', error: error.message })
  }
})

app.get('/test_orders', (_req, res) => {
  res.json({ orders: activeOrders.map(a => a.customer_name) })
})

app.get('/menu', (_req, res) => {
  res.json(getFullMenu())
})

app.post('/menu', (req, res) => {
  try {
    updateCustomMenu(req.body);
    res.json({ success: true });
  } catch (e) {
    res.status(500).json({ error: 'Failed to update menu' });
  }
})

app.get('/network_status', (_req, res) => {
  const os = require('os')
  const nets = os.networkInterfaces()
  let localIp = '127.0.0.1'
  for (const name of Object.keys(nets)) {
    for (const net of nets[name]) {
      if (net.family === 'IPv4' && !net.internal) {
        localIp = net.address
        break
      }
    }
  }
  res.json({
    ip: localIp,
    port: 5000,
    connectedDevices: getConnectedPhones()
  })
})

app.get('/past_orders', (_req, res) => {
  res.json(pastOrders)
})

app.get('/spotify/login', (_req, res) => {
  const SPOTIFY_CLIENT_ID = systemSettings["SPOTIFY_CLIENT_ID"] || ""
  if (!SPOTIFY_CLIENT_ID) {
    res.send("Lutfen once Kasa ayarlarindan Client ID girin.")
    return
  }
  const scope = "streaming user-read-email user-read-private user-read-playback-state user-modify-playback-state"
  const authUrl = `https://accounts.spotify.com/authorize?response_type=code&client_id=${SPOTIFY_CLIENT_ID}&scope=${encodeURIComponent(scope)}&redirect_uri=http://127.0.0.1:5000/spotify/callback`
  res.redirect(authUrl)
})

app.get('/spotify/callback', async (req, res) => {
  const code = req.query.code as string
  if (!code) {
    res.send("Spotify baglantisi reddedildi.")
    return
  }

  const SPOTIFY_CLIENT_ID = systemSettings["SPOTIFY_CLIENT_ID"] || ""
  const SPOTIFY_CLIENT_SECRET = systemSettings["SPOTIFY_CLIENT_SECRET"] || ""
  const authHeader = Buffer.from(`${SPOTIFY_CLIENT_ID}:${SPOTIFY_CLIENT_SECRET}`).toString('base64')

  try {
    const response = await axios.post("https://accounts.spotify.com/api/token", 
      new URLSearchParams({
        grant_type: "authorization_code",
        code,
        redirect_uri: "http://127.0.0.1:5000/spotify/callback"
      }).toString(),
      {
        headers: {
          "Authorization": `Basic ${authHeader}`,
          "Content-Type": "application/x-www-form-urlencoded"
        }
      }
    )

    systemSettings["SPOTIFY_ACCESS_TOKEN"] = response.data.access_token
    systemSettings["SPOTIFY_REFRESH_TOKEN"] = response.data.refresh_token
    saveSettings()
    res.send("Spotify basariyla baglandi! Kasa uygulamasina donebilirsiniz. Bu pencereyi kapatabilirsiniz.")
  } catch (error: any) {
    res.send(`Hata: ${error.response?.data ? JSON.stringify(error.response.data) : error.message}`)
  }
})

app.get('/spotify/token', async (_req, res) => {
  let accessToken = systemSettings["SPOTIFY_ACCESS_TOKEN"] || ""
  let refreshToken = systemSettings["SPOTIFY_REFRESH_TOKEN"] || ""
  
  if (!accessToken || !refreshToken) {
    res.status(401).json({ error: "not_logged_in" })
    return
  }

  try {
    await axios.get("https://api.spotify.com/v1/me", {
      headers: { "Authorization": `Bearer ${accessToken}` }
    })
    res.json({ access_token: accessToken })
  } catch (err: any) {
    if (err.response && err.response.status === 401) {
      const SPOTIFY_CLIENT_ID = systemSettings["SPOTIFY_CLIENT_ID"] || ""
      const SPOTIFY_CLIENT_SECRET = systemSettings["SPOTIFY_CLIENT_SECRET"] || ""
      const authHeader = Buffer.from(`${SPOTIFY_CLIENT_ID}:${SPOTIFY_CLIENT_SECRET}`).toString('base64')

      try {
        const refRes = await axios.post("https://accounts.spotify.com/api/token", 
          new URLSearchParams({
            grant_type: "refresh_token",
            refresh_token: refreshToken
          }).toString(),
          {
            headers: {
              "Authorization": `Basic ${authHeader}`,
              "Content-Type": "application/x-www-form-urlencoded"
            }
          }
        )
        systemSettings["SPOTIFY_ACCESS_TOKEN"] = refRes.data.access_token
        if (refRes.data.refresh_token) {
          systemSettings["SPOTIFY_REFRESH_TOKEN"] = refRes.data.refresh_token
        }
        saveSettings()
        res.json({ access_token: systemSettings["SPOTIFY_ACCESS_TOKEN"] })
      } catch (refErr) {
        res.status(401).json({ error: "refresh_failed" })
      }
    } else {
      res.status(500).json({ error: err.message })
    }
  }
})

export function startServer(port = 5000) {
  server.listen(port, '0.0.0.0', () => {
    // Server started silently
  })
}
