import { contextBridge, ipcRenderer } from 'electron'
import { electronAPI } from '@electron-toolkit/preload'

// Custom APIs for renderer
const api = {
  getOrders: () => ipcRenderer.invoke('get-orders'),
  getMenu: () => ipcRenderer.invoke('get-menu'),
  getSettings: () => ipcRenderer.invoke('get-settings'),
  getPrinters: () => ipcRenderer.invoke('get-printers'),
  getNextQueueNo: () => ipcRenderer.invoke('get-next-queue-no'),
  saveOrders: (orders: any[]) => ipcRenderer.send('save-orders', orders),
  saveSettings: (settings: any) => ipcRenderer.send('save-settings', settings),
  printReceipt: (data: any) => ipcRenderer.send('print-receipt', data),
  exitApp: () => ipcRenderer.send('exit-app'),
  sendUpdateToPhones: (url: string) => ipcRenderer.send('send-update-to-phones', url),
  updateDailyTotal: (total: number) => ipcRenderer.send('update-daily-total', total),
  savePastOrder: (order: any) => ipcRenderer.send('save-past-order', order),
  deletePastOrder: (index: number) => ipcRenderer.send('delete-past-order', index),
  clearPastOrders: () => ipcRenderer.send('clear-past-orders'),
  getNetworkStatus: () => ipcRenderer.invoke('get-network-status'),
  getPastOrders: () => ipcRenderer.invoke('get-past-orders'),
  saveMenu: (menu: any) => ipcRenderer.send('save-menu', menu),
  
  onServerEvent: (callback: (action: string, data?: any) => void) => {
    const subscription = (_event: any, args: any) => callback(args.action, args.data)
    ipcRenderer.on('server-event', subscription)
    return subscription
  },
  offServerEvent: (subscription: any) => {
    ipcRenderer.removeListener('server-event', subscription)
  },
  updatePrice: (productName: string, portion: string, price: number) => ipcRenderer.invoke('update-price', { productName, portion, price })
}

if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld('electron', electronAPI)
    contextBridge.exposeInMainWorld('api', api)
  } catch (error) {
    console.error(error)
  }
} else {
  // @ts-ignore (define in dts)
  window.electron = electronAPI
  // @ts-ignore (define in dts)
  window.api = api
}

