import { useEffect } from 'react'
import { useStore } from './store'
import Sidebar from './components/Sidebar'
import MainPanel from './components/MainPanel'
import CartPanel from './components/CartPanel'
import OrderModal from './components/OrderModal'
import SettingsModal from './components/SettingsModal'

function App() {
  const { setOrders, setMenu } = useStore()

  useEffect(() => {
    const handleOrders = (orders: any[]) => {
      setOrders(orders)
      // Siparişlerdeki en yüksek "Sıra X" numarasını bulup sequence'ı ayarla
      let maxSira = 0
      orders.forEach((o: any) => {
        if (o.customer_name && o.customer_name.startsWith('Sıra ')) {
          const num = parseInt(o.customer_name.replace('Sıra ', ''), 10)
          if (!isNaN(num) && num > maxSira) {
            maxSira = num
          }
        }
      })
      useStore.setState({ orderSequence: maxSira + 1 })
    }

    // Initial fetch
    window.api.getOrders().then(handleOrders)
    window.api.getMenu().then(setMenu)

    // Listen to IPC
    const handleServerEvent = (action: string, data?: any) => {
      // Telefonda "Ödendi" (close_bill) denildiğinde gelen tutarı günlük kazanca ekle
      if (action === 'order_deleted' && data && data.totalAmount) {
        const currentTotal = parseFloat(localStorage.getItem('dailyTotal') || '0')
        localStorage.setItem('dailyTotal', (currentTotal + data.totalAmount).toString())
        window.dispatchEvent(new Event('daily-total-updated'))
      }

      if (action === 'request_update' || action === 'order_received' || action === 'order_deleted' || action === 'update_status' || action === 'new_order') {
        window.api.getOrders().then(handleOrders)
      }

      if (action === 'print_receipt' && data && data.customerName) {
        window.api.getOrders().then(orders => {
          const order = orders.find(o => o.customer_name === data.customerName)
          if (order) {
            window.api.printReceipt(order)
          }
        })
      }
    }

    const sub = window.api.onServerEvent(handleServerEvent)
    return () => {
      window.api.offServerEvent(sub)
    }
  }, [setOrders, setMenu])

  return (
    <div className="app-container">
      <Sidebar />
      <MainPanel />
      <CartPanel />
      <OrderModal />
      <SettingsModal />
    </div>
  )
}

export default App
