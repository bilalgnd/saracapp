import { app, shell, BrowserWindow, ipcMain, globalShortcut } from 'electron'
import { join } from 'path'
import { autoUpdater } from 'electron-updater'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import icon from '../../resources/icon.png?asset'
import { initializeModels, getFullMenu, activeOrders, saveOrders, systemSettings, saveSettings, getNextQueueNo, updatePrice, pastOrders, updateCustomMenu, savePastOrders } from './models'
import { startServer, setMainWindow, broadcastUpdateToPhones, broadcastMessageToPhones, setGlobalDailyTotal, getConnectedPhones } from './server'
import { printReceipt } from './printer'

let mainWindow: BrowserWindow
let isQuitting = false

async function createWindow(): Promise<void> {
  // Initialize persistence before UI
  await initializeModels()
  
  // Start Express API & Websocket Server
  startServer(5000)

  mainWindow = new BrowserWindow({
    width: 1366,
    height: 768,
    minWidth: 1024,
    minHeight: 600,
    show: false,
    autoHideMenuBar: true,
    ...(process.platform === 'linux' ? { icon } : {}),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false
    }
  })

  setMainWindow(mainWindow)

  mainWindow.on('ready-to-show', () => {
    if (!process.argv.includes('--hidden')) {
      mainWindow.show()
    }
  })

  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault()
      mainWindow.hide()
    }
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

app.whenReady().then(() => {
  electronApp.setAppUserModelId('com.saracoglu.pos')
  
  if (!is.dev) {
    autoUpdater.checkForUpdatesAndNotify()
  }

  app.setLoginItemSettings({
    openAtLogin: true,
    args: ['--hidden']
  })

  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  // ---- IPC Handlers ----
  ipcMain.handle('get-orders', () => activeOrders)
  ipcMain.handle('get-menu', () => getFullMenu())
  ipcMain.handle('get-printers', async () => await mainWindow.webContents.getPrintersAsync())
  ipcMain.handle('get-next-queue-no', () => getNextQueueNo())
  
  ipcMain.handle('get-settings', () => systemSettings)
  ipcMain.on('save-settings', (_, settings) => {
    Object.assign(systemSettings, settings)
    saveSettings()
  })

  ipcMain.handle('get-past-orders', () => pastOrders)
  
  ipcMain.handle('get-network-status', () => {
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
    return { ip: localIp, port: 5000, connectedDevices: getConnectedPhones() }
  })

  ipcMain.on('save-menu', (_, newMenu) => {
    updateCustomMenu(newMenu)
  })

  ipcMain.on('update-daily-total', (_, total) => {
    // Sync daily total to server
    setGlobalDailyTotal(total)
  })

  ipcMain.on('save-past-order', (_, order) => {
    pastOrders.unshift(order)
    if (pastOrders.length > 500) pastOrders.pop()
    savePastOrders()
  })

  ipcMain.on('delete-past-order', (_, index) => {
    if (index >= 0 && index < pastOrders.length) {
      pastOrders.splice(index, 1)
      savePastOrders()
    }
  })

  ipcMain.on('clear-past-orders', () => {
    pastOrders.length = 0
    savePastOrders()
  })

  ipcMain.handle('update-price', (_, { productName, portion, price }) => {
    updatePrice(productName, portion, price)
    broadcastUpdateToPhones()
    return true
  })

  ipcMain.on('save-orders', (_, newOrders) => {
    activeOrders.length = 0
    activeOrders.push(...newOrders)
    saveOrders()
    broadcastUpdateToPhones()
  })

  ipcMain.on('print-receipt', async (_, data) => {
    const custName = data.customerName || data.customer_name || 'Bilinmiyor'
    const total = data.totalAmount || data.total_amount || 0
    await printReceipt(custName, new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }), data.items || [], total, data.order_note || "")
  })



  ipcMain.on('send-update-to-phones', (_, url) => {
    broadcastMessageToPhones({ type: "apk_guncelleme", url })
  })

  ipcMain.on('exit-app', () => {
    isQuitting = true
    app.quit()
  })

  globalShortcut.register('CommandOrControl+Alt+S', () => {
    if (mainWindow) {
      mainWindow.show()
      mainWindow.focus()
    }
  })

  createWindow()

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('before-quit', () => {
  isQuitting = true
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
