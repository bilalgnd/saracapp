import { useState, useEffect } from 'react'
import { useStore } from '../store'
import { LayoutGrid, Beef, Drumstick, Tags, Coffee, Settings, LogOut, RefreshCcw } from 'lucide-react'

export default function Sidebar() {
  const { activeTab, setActiveTab, menu } = useStore()

  const tabs = [
    { name: 'MASALAR', icon: <LayoutGrid size={20} /> }
  ]
  
  if (menu && menu.categories) {
    menu.categories.forEach(cat => {
      let icon = <Tags size={20} />
      const nameLower = cat.name.toLowerCase()
      if (nameLower.includes('et')) icon = <Beef size={20} />
      if (nameLower.includes('tavuk')) icon = <Drumstick size={20} />
      if (nameLower.includes('kampanya')) icon = <Tags size={20} />
      if (nameLower.includes('içecek') || nameLower.includes('icecek')) icon = <Coffee size={20} />
      
      tabs.push({ name: cat.name.toUpperCase(), icon })
    })
  }

  const [dailyTotal, setDailyTotal] = useState(0)

  useEffect(() => {
    const total = parseFloat(localStorage.getItem('dailyTotal') || '0')
    setDailyTotal(total)

    const handleUpdate = () => {
      setDailyTotal(parseFloat(localStorage.getItem('dailyTotal') || '0'))
    }

    window.addEventListener('daily-total-updated', handleUpdate)

    return () => {
      window.removeEventListener('daily-total-updated', handleUpdate)
    }
  }, [])

  // Sync dailyTotal to backend for TV Mode via IPC
  useEffect(() => {
    if (window.api && window.api.updateDailyTotal) {
      window.api.updateDailyTotal(dailyTotal)
    }
  }, [dailyTotal])

  const resetDailyTotal = () => {
    if (confirm('Günlük kazancı sıfırlamak istediğinize emin misiniz?')) {
      localStorage.setItem('dailyTotal', '0')
      setDailyTotal(0)
    }
  }



  const handleExit = () => {
    window.api.exitApp()
  }

  return (
    <div className="sidebar">
      <div className="logo-container">
        <div className="logo-title">SARAÇOĞLU</div>
        <div className="logo-subtitle">POS DASHBOARD</div>
      </div>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {tabs.map((tab, idx) => (
          <button
            key={idx}
            className={`nav-btn ${activeTab === idx ? 'active' : ''}`}
            onClick={() => setActiveTab(idx)}
          >
            {tab.icon} {tab.name}
          </button>
        ))}

        <div style={{ 
          marginTop: '20px', 
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '10px'
        }}>
          <div style={{ color: 'var(--success)', fontSize: '18px', fontWeight: 'bold' }}>{dailyTotal.toLocaleString('tr-TR')} ₺</div>
          <button 
            style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '5px', display: 'flex', alignItems: 'center' }}
            onClick={resetDailyTotal}
            title="Günlük Kazancı Sıfırla"
          >
            <RefreshCcw size={16} />
          </button>
        </div>
      </div>

      <div className="sidebar-bottom">
        <button 
          className="btn" 
          style={{ height: 45, backgroundColor: 'var(--bg-panel)', color: 'white' }}
          onClick={() => window.dispatchEvent(new CustomEvent('open-settings-modal'))}
        >
          <Settings size={20} style={{ marginRight: 8 }} /> Sistem Ayarları
        </button>
        <button 
          className="btn btn-danger" 
          style={{ height: 45 }}
          onClick={handleExit}
        >
          <LogOut size={20} style={{ marginRight: 8 }} /> Çıkış
        </button>
      </div>
    </div>
  )
}
