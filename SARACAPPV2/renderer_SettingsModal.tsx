import { useState, useEffect } from 'react'
import { useStore } from '../store'

export default function SettingsModal() {
  const [isOpen, setIsOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('general')
  
  const [settings, setSettings] = useState<any>({})
  const [printers, setPrinters] = useState<any[]>([])
  
  const [latestRelease, setLatestRelease] = useState<any>(null)
  const [isCheckingUpdate, setIsCheckingUpdate] = useState(false)
  
  const [networkStatus, setNetworkStatus] = useState<any>(null)
  const [pastOrders, setPastOrders] = useState<any[]>([])
  const [menuData, setMenuData] = useState<any>(null)

  // Custom Prompt States
  const [promptData, setPromptData] = useState<{ type: 'add' | 'edit' | 'color' | 'textColor' | 'globalTextColor' | 'addCategory' | 'renameCategory', category?: string, idx?: number, catIdx?: number, oldName?: string, title: string } | null>(null)
  const [inputVal1, setInputVal1] = useState('') // Used for Product Name or Color
  const [portions, setPortions] = useState<{portion: string, price: string}[]>([{portion: 'Standart', price: ''}])
  
  // Drag and Drop State
  const [draggedItem, setDraggedItem] = useState<{ catIdx: number, idx: number } | null>(null)
  


  useEffect(() => {
    const handleOpen = () => {
      window.api.getSettings().then((data) => setSettings(data || {}))
      fetchNetworkStatus()
      fetchPastOrders()
      fetchMenu()
      setIsOpen(true)
    }
    window.addEventListener('open-settings-modal', handleOpen)
    return () => window.removeEventListener('open-settings-modal', handleOpen)
  }, [])

  const fetchNetworkStatus = async () => {
    try {
      const res = await window.api.getNetworkStatus()
      setNetworkStatus(res)
    } catch (e) { console.error(e) }
  }

  const fetchPastOrders = async () => {
    try {
      const res = await window.api.getPastOrders()
      setPastOrders(res || [])
    } catch (e) { console.error(e) }
  }

  const handleDeletePastOrder = (index: number) => {
    if (confirm('Bu siparişi geçmişten silmek istediğinize emin misiniz?')) {
      if (window.api && window.api.deletePastOrder) {
        window.api.deletePastOrder(index)
        setPastOrders(prev => prev.filter((_, i) => i !== index))
      }
    }
  }

  const handleClearPastOrders = () => {
    if (confirm('Tüm geçmiş siparişleri kalıcı olarak silmek istediğinize emin misiniz? Bu işlem geri alınamaz!')) {
      if (window.api && window.api.clearPastOrders) {
        window.api.clearPastOrders()
        setPastOrders([])
      }
    }
  }

  const fetchMenu = async () => {
    try {
      const res = await window.api.getMenu()
      setMenuData(res)
    } catch (e) { console.error(e) }
  }

  if (!isOpen) return null

  const handleSaveSettings = () => {
    window.api.saveSettings(settings)
    alert("Ayarlar kaydedildi!")
  }

  const handleSettingChange = (key: string, value: string) => {
    setSettings((prev: any) => ({ ...prev, [key]: value }))
  }

  const loadPrinters = async () => {
    const prns = await window.api.getPrinters()
    setPrinters(prns)
  }

  const selectPrinter = (printerName: string) => {
    handleSettingChange('YAZICI_ADI', printerName)
    window.api.saveSettings({ ...settings, YAZICI_ADI: printerName })
    alert(`Yazıcı seçildi: ${printerName}`)
  }

  const triggerSpotifyLogin = () => window.open('http://127.0.0.1:5000/spotify/login', '_blank')
  const openWebPanel = () => window.open('http://127.0.0.1:5000/', '_blank')

  const checkUpdates = async () => {
    setIsCheckingUpdate(true)
    try {
      const res = await fetch('https://api.github.com/repos/bilalgnd/saracapp/releases/latest', { cache: 'no-store' })
      if (res.ok) {
        const data = await res.json()
        setLatestRelease(data)
      }
    } catch (e) {
      console.error("Guncelleme kontrolu basarisiz", e)
    } finally {
      setIsCheckingUpdate(false)
    }
  }

  const sendUpdateToPhones = (url: string) => {
    if (confirm("Bu guncellemeyi (APK) tum garson telefonlarina yollamak istediginize emin misiniz?")) {
      window.api.sendUpdateToPhones(url)
      alert("Guncelleme komutu tum telefonlara gonderildi!")
    }
  }
  
  const openAddCategoryPrompt = () => {
    setInputVal1('')
    setPromptData({ type: 'addCategory', title: 'Yeni Kategori Ekle' })
  }

  const openRenameCategoryPrompt = (catIdx: number, oldName: string) => {
    setInputVal1(oldName)
    setPromptData({ type: 'renameCategory', catIdx, title: 'Kategori Adını Değiştir', oldName })
  }

  const handleDeleteCategory = (catIdx: number, catName: string) => {
    if (!confirm(`'${catName}' kategorisini ve içindeki TÜM ürünleri silmek istediğinize emin misiniz?`)) return
    const newMenu = { ...menuData }
    newMenu.categories = newMenu.categories.filter((_: any, i: number) => i !== catIdx)
    
    setMenuData(newMenu)
    useStore.getState().setMenu(newMenu)
    
    try {
      if (window.api && window.api.saveMenu) {
        window.api.saveMenu(newMenu)
      }
    } catch (e) {
      console.error("Save menu error", e)
    }
  }

  const openAddProductPrompt = (catIdx: number) => {
    setInputVal1('')
    setPortions([{portion: 'Standart', price: ''}])
    setPromptData({ type: 'add', catIdx, title: 'Yeni Ürün Ekle' })
  }

  const openEditProductPrompt = (catIdx: number, idx: number, prod: any) => {
    setInputVal1(prod.name)
    setPortions(prod.options.map((o: any) => ({ portion: o.portion, price: o.price.toString() })))
    setPromptData({ type: 'edit', catIdx, idx, title: 'Ürünü Düzenle' })
  }

  const openColorPrompt = (catIdx: number, idx: number, currentColor: string) => {
    setInputVal1(currentColor || '#333333')
    setPromptData({ type: 'color', catIdx, idx, title: 'Ürün Arka Plan Rengini Değiştir' })
  }

  const openTextColorPrompt = (catIdx: number, idx: number, currentTextColor: string) => {
    setInputVal1(currentTextColor || '#FFFFFF')
    setPromptData({ type: 'textColor', catIdx, idx, title: 'Ürün Yazı Rengini Değiştir' })
  }

  const openGlobalTextColorPrompt = () => {
    setInputVal1('')
    setPromptData({ type: 'globalTextColor', title: 'Tüm Menünün Yazı Rengini Değiştir' })
  }

  const handleDeleteProduct = (catIdx: number, idx: number) => {
    if (!confirm("Bu ürünü silmek istediğinize emin misiniz?")) return
    const newMenu = { ...menuData }
    const newCatItems = newMenu.categories[catIdx].items.filter((_: any, i: number) => i !== idx)
    newMenu.categories[catIdx].items = newCatItems
    
    setMenuData(newMenu)
    useStore.getState().setMenu(newMenu)
    
    try {
      if (window.api && window.api.saveMenu) {
        window.api.saveMenu(newMenu)
      }
    } catch (e) {
      console.error("Save menu error", e)
    }
  }

  // Drag and Drop Handlers
  const handleDragStart = (catIdx: number, idx: number) => {
    setDraggedItem({ catIdx, idx })
  }

  const handleDragOver = (e: React.DragEvent, _catIdx: number) => {
    e.preventDefault() // Gerekli: drop işlemine izin ver
  }

  const handleDrop = (catIdx: number, dropIdx: number) => {
    if (!draggedItem || draggedItem.catIdx !== catIdx || draggedItem.idx === dropIdx) {
      setDraggedItem(null)
      return
    }

    const newMenu = { ...menuData }
    const catItems = [...newMenu.categories[catIdx].items]
    
    // Öğeyi eski yerinden çıkar
    const [removedItem] = catItems.splice(draggedItem.idx, 1)
    // Yeni yerine ekle
    catItems.splice(dropIdx, 0, removedItem)
    
    newMenu.categories[catIdx].items = catItems
    setMenuData(newMenu)
    useStore.getState().setMenu(newMenu)
    
    try {
      if (window.api && window.api.saveMenu) {
        window.api.saveMenu(newMenu)
      }
    } catch (e) {}
    
    setDraggedItem(null)
  }

  const submitPrompt = () => {
    if (!promptData) return
    const newMenu = { ...menuData }
    
    if (promptData.type === 'add') {
      if (!inputVal1 || portions.some(p => !p.portion || !p.price)) {
        alert('Lütfen ürün adını ve tüm porsiyon/fiyat bilgilerini eksiksiz girin.')
        return
      }
      const newItem = {
        name: inputVal1,
        color: '#333333',
        textColor: '#FFFFFF',
        options: portions.map(p => ({ portion: p.portion, price: parseInt(p.price) }))
      }
      newMenu.categories[promptData.catIdx!].items = [newItem, ...newMenu.categories[promptData.catIdx!].items]
    } 
    else if (promptData.type === 'edit') {
      if (!inputVal1 || portions.some(p => !p.portion || !p.price)) {
        alert('Lütfen ürün adını ve tüm porsiyon/fiyat bilgilerini eksiksiz girin.')
        return
      }
      newMenu.categories[promptData.catIdx!].items[promptData.idx!] = {
        ...newMenu.categories[promptData.catIdx!].items[promptData.idx!],
        name: inputVal1,
        options: portions.map(p => ({ portion: p.portion, price: parseInt(p.price) }))
      }
    }
    else if (promptData.type === 'color') {
      if (!inputVal1) return
      newMenu.categories[promptData.catIdx!].items[promptData.idx!].color = inputVal1
    }
    else if (promptData.type === 'textColor') {
      if (!inputVal1) return
      newMenu.categories[promptData.catIdx!].items[promptData.idx!].textColor = inputVal1
    }
    else if (promptData.type === 'globalTextColor') {
      if (!inputVal1) return
      if (newMenu.categories) {
        newMenu.categories.forEach((cat: any) => {
          cat.items = cat.items.map((item: any) => ({ ...item, textColor: inputVal1 }))
        })
      }
    }
    else if (promptData.type === 'addCategory') {
      if (!inputVal1) return
      if (!newMenu.categories) newMenu.categories = []
      newMenu.categories.push({ id: `cat_${Date.now()}`, name: inputVal1, items: [] })
    }
    else if (promptData.type === 'renameCategory') {
      if (!inputVal1) return
      newMenu.categories[promptData.catIdx!].name = inputVal1
    }
    
    setMenuData(newMenu)
    useStore.getState().setMenu(newMenu)
    
    try {
      if (window.api && window.api.saveMenu) {
        window.api.saveMenu(newMenu)
      }
    } catch (e) {
      console.error("Save menu error", e)
    }
    
    setPromptData(null)
  }

  return (
    <div className="settings-overlay" onClick={() => setIsOpen(false)}>
      <div className="settings-modal" onClick={e => e.stopPropagation()}>
        <button className="settings-close-btn" onClick={() => setIsOpen(false)}>✕</button>
        
        {/* Custom Prompt Modal (Overlay over settings modal) */}
        {promptData && (
          <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.85)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 100 }}>
            <div style={{ backgroundColor: '#1A1A1A', padding: 30, borderRadius: 10, width: 450, border: '1px solid #333', boxShadow: '0 10px 30px rgba(0,0,0,0.5)', maxHeight: '80vh', overflowY: 'auto' }}>
              <h3 style={{ color: 'white', marginBottom: 20 }}>{promptData.title}</h3>
              
              {promptData.type === 'addCategory' || promptData.type === 'renameCategory' ? (
                <>
                  <label style={{ display: 'block', color: '#ccc', marginBottom: 5 }}>Kategori Adı:</label>
                  <input autoFocus className="settings-input" value={inputVal1} onChange={e => setInputVal1(e.target.value)} placeholder="Örn: Tatlılar" />
                </>
              ) : promptData.type === 'add' || promptData.type === 'edit' ? (
                <>
                  <label style={{ display: 'block', color: '#ccc', marginBottom: 5 }}>Ürün Adı:</label>
                  <input autoFocus className="settings-input" value={inputVal1} onChange={e => setInputVal1(e.target.value)} placeholder="Örn: Et Döner" />
                  
                  <label style={{ display: 'block', color: '#ccc', marginBottom: 5, marginTop: 15 }}>Porsiyonlar ve Fiyatlar:</label>
                  {portions.map((p, i) => (
                    <div key={i} style={{ display: 'flex', gap: 10, marginBottom: 10 }}>
                      <input className="settings-input" style={{ marginBottom: 0, flex: 1 }} value={p.portion} onChange={e => {
                        const newP = [...portions]; newP[i].portion = e.target.value; setPortions(newP)
                      }} placeholder="Porsiyon (Örn: Dürüm, 100gr)" />
                      <input type="number" className="settings-input" style={{ marginBottom: 0, width: 100 }} value={p.price} onChange={e => {
                        const newP = [...portions]; newP[i].price = e.target.value; setPortions(newP)
                      }} placeholder="Fiyat (TL)" />
                      {portions.length > 1 && (
                        <button className="settings-btn danger" style={{ padding: '0 15px' }} onClick={() => setPortions(portions.filter((_, idx) => idx !== i))}>X</button>
                      )}
                    </div>
                  ))}
                  <button className="settings-btn" style={{ width: '100%', marginTop: 5, padding: 8, fontSize: 13, borderStyle: 'dashed' }} onClick={() => setPortions([...portions, {portion: '', price: ''}])}>+ Yeni Gramaj/Porsiyon Ekle</button>
                </>
              ) : (
                <>
                  <label style={{ display: 'block', color: '#ccc', marginBottom: 5 }}>Yeni Renk Kodu (Ad veya HEX):</label>
                  <input autoFocus className="settings-input" value={inputVal1} onChange={e => setInputVal1(e.target.value)} placeholder="Örn: #FFFFFF, black, white" />
                  <div style={{ display: 'flex', gap: 10, marginTop: 10 }}>
                    <button style={{ flex: 1, height: 30, backgroundColor: '#FFFFFF', border: 'none', color: 'black' }} onClick={() => setInputVal1('#FFFFFF')}>Beyaz</button>
                    <button style={{ flex: 1, height: 30, backgroundColor: '#000000', border: '1px solid #333', color: 'white' }} onClick={() => setInputVal1('#000000')}>Siyah</button>
                    {promptData.type === 'color' && (
                      <>
                        <button style={{ flex: 1, height: 30, backgroundColor: '#D32F2F', border: 'none' }} onClick={() => setInputVal1('#D32F2F')} />
                        <button style={{ flex: 1, height: 30, backgroundColor: '#388E3C', border: 'none' }} onClick={() => setInputVal1('#388E3C')} />
                        <button style={{ flex: 1, height: 30, backgroundColor: '#F9A825', border: 'none' }} onClick={() => setInputVal1('#F9A825')} />
                      </>
                    )}
                  </div>
                </>
              )}
              
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 25 }}>
                <button className="settings-btn" onClick={() => setPromptData(null)}>İptal</button>
                <button className="settings-btn success" onClick={submitPrompt}>Onayla</button>
              </div>
            </div>
          </div>
        )}

        <div className="settings-sidebar">
          <div className="settings-sidebar-header">
            <h2>Ayarlar</h2>
          </div>
          <button className={`settings-tab ${activeTab === 'general' ? 'active' : ''}`} onClick={() => setActiveTab('general')}>Genel</button>
          <button className={`settings-tab ${activeTab === 'menu' ? 'active' : ''}`} onClick={() => setActiveTab('menu')}>Menü Yönetimi</button>
          <button className={`settings-tab ${activeTab === 'past_orders' ? 'active' : ''}`} onClick={() => setActiveTab('past_orders')}>Geçmiş Siparişler</button>
          <button className={`settings-tab ${activeTab === 'network' ? 'active' : ''}`} onClick={() => { setActiveTab('network'); fetchNetworkStatus(); }}>Sistem & Ağ</button>
          <button className={`settings-tab ${activeTab === 'printer' ? 'active' : ''}`} onClick={() => { setActiveTab('printer'); loadPrinters(); }}>Yazıcı</button>
          <button className={`settings-tab ${activeTab === 'spotify' ? 'active' : ''}`} onClick={() => setActiveTab('spotify')}>Spotify API</button>
          <button className={`settings-tab ${activeTab === 'updates' ? 'active' : ''}`} onClick={() => { setActiveTab('updates'); checkUpdates(); }}>Güncellemeler</button>
        </div>

        <div className="settings-content">
          {activeTab === 'general' && (
            <div>
              <div className="settings-section-title">Genel Ayarlar</div>
              <div className="settings-card">
                <div className="settings-card-title">Hızlı İşlemler</div>
                <div className="settings-row">
                  <button className="settings-btn" onClick={openWebPanel}>Web Paneli'ni Aç</button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'menu' && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 25, borderBottom: '1px solid #2A2A2A', paddingBottom: 10 }}>
                <div className="settings-section-title" style={{ borderBottom: 'none', paddingBottom: 0, marginBottom: 0 }}>Menü Yönetimi</div>
                <button className="settings-btn" style={{ padding: '8px 15px', fontSize: 13, borderStyle: 'dashed' }} onClick={openGlobalTextColorPrompt}>Tüm Ürünlerin Yazı Rengini Değiştir</button>
              </div>
              
              <div style={{ fontSize: 12, color: '#888', marginBottom: 20 }}>💡 İpucu: Ürünlerin sırasını değiştirmek için tablonun en sağındaki "☰" (Sürükle) simgesinden tutup yukarı veya aşağı kaydırabilirsiniz. Yeni kategori eklemek için aşağıdaki butonu kullanın.</div>
              
              {menuData?.categories?.map((cat: any, catIdx: number) => (
                <div key={cat.id || catIdx} className="settings-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 15 }}>
                    <div className="settings-card-title" style={{ margin: 0, textTransform: 'capitalize', display: 'flex', gap: '10px', alignItems: 'center' }}>
                      Kategori: {cat.name}
                      <button className="settings-btn primary" style={{ padding: '3px 8px', fontSize: 11 }} onClick={() => openRenameCategoryPrompt(catIdx, cat.name)}>Adını Düzenle</button>
                      <button className="settings-btn danger" style={{ padding: '3px 8px', fontSize: 11 }} onClick={() => handleDeleteCategory(catIdx, cat.name)}>Kategoriyi Sil</button>
                    </div>
                    <button className="settings-btn success" style={{ padding: '5px 10px', fontSize: 12 }} onClick={() => openAddProductPrompt(catIdx)}>+ Yeni Ürün</button>
                  </div>
                  <table className="settings-table">
                    <thead>
                      <tr>
                        <th>Ürün Adı</th>
                        <th>Renkler</th>
                        <th>İşlem</th>
                        <th style={{ width: 40, textAlign: 'center' }}>Sıra</th>
                      </tr>
                    </thead>
                    <tbody>
                      {cat.items?.map((prod: any, i: number) => (
                        <tr 
                          key={i}
                          draggable
                          onDragStart={() => handleDragStart(catIdx, i)}
                          onDragOver={(e) => handleDragOver(e, catIdx)}
                          onDrop={() => handleDrop(catIdx, i)}
                          style={{ 
                            backgroundColor: draggedItem?.catIdx === catIdx && draggedItem?.idx === i ? '#333' : 'transparent',
                            opacity: draggedItem?.catIdx === catIdx && draggedItem?.idx === i ? 0.5 : 1
                          }}
                        >
                          <td>
                            <div style={{ fontWeight: 600 }}>{prod.name}</div>
                            <div style={{ fontSize: 11, color: '#888', marginTop: 3 }}>
                              {prod.options?.map((o:any) => `${o.portion}: ${o.price}₺`).join(' | ')}
                            </div>
                          </td>
                          <td>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 5 }}>
                              <div style={{ width: 14, height: 14, backgroundColor: prod.color || '#333', borderRadius: 4 }}></div>
                              <span style={{ fontSize: 11, color: '#aaa' }}>Arka: {prod.color || '#333'}</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                              <div style={{ width: 14, height: 14, backgroundColor: prod.textColor || '#fff', borderRadius: 4, border: '1px solid #555' }}></div>
                              <span style={{ fontSize: 11, color: '#aaa' }}>Yazı: {prod.textColor || '#fff'}</span>
                            </div>
                          </td>
                          <td>
                            <div style={{ display: 'flex', gap: 5 }}>
                              <button className="settings-btn primary" style={{ padding: '5px 10px', fontSize: 11, color: 'black' }} onClick={() => openEditProductPrompt(catIdx, i, prod)}>Düzenle</button>
                              <button className="settings-btn danger" style={{ padding: '5px 10px', fontSize: 11 }} onClick={() => handleDeleteProduct(catIdx, i)}>Sil</button>
                              <button className="settings-btn" style={{ padding: '5px 10px', fontSize: 11 }} onClick={() => openColorPrompt(catIdx, i, prod.color)}>Arka Plan</button>
                              <button className="settings-btn" style={{ padding: '5px 10px', fontSize: 11 }} onClick={() => openTextColorPrompt(catIdx, i, prod.textColor)}>Yazı Rengi</button>
                            </div>
                          </td>
                          <td style={{ textAlign: 'center', cursor: 'grab', fontSize: 18, color: '#666' }}>
                            ☰
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ))}

              <div style={{ display: 'flex', justifyContent: 'center', marginTop: 20 }}>
                <button className="settings-btn success" style={{ padding: '10px 20px', fontSize: 14 }} onClick={openAddCategoryPrompt}>+ YENİ KATEGORİ EKLE</button>
              </div>
            </div>
          )}

          {activeTab === 'past_orders' && (
            <div>
              <div className="settings-section-title">Geçmiş Siparişler <span style={{ fontSize: 14, color: '#888' }}>(Son 500)</span></div>
              <div className="settings-card" style={{ padding: 0, border: 'none' }}>
                <table className="settings-table">
                  <thead>
                    <tr>
                      <th>Tarih</th>
                      <th>Müşteri / Masa</th>
                      <th>Tutar</th>
                      <th>Durum</th>
                      <th style={{ textAlign: 'right' }}>İşlem</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pastOrders.length === 0 && <tr><td colSpan={5} style={{ textAlign: 'center' }}>Kayıt bulunamadı.</td></tr>}
                    {pastOrders.map((o, i) => {
                      const dt = o.completedAt ? new Date(o.completedAt) : new Date();
                      return (
                        <tr key={i}>
                          <td>{dt.toLocaleTimeString()}</td>
                          <td>{o.customer_name}</td>
                          <td style={{ color: '#4CAF50', fontWeight: 'bold' }}>{o.total_amount} ₺</td>
                          <td><span style={{ color: o.status === 'İptal' ? '#F44336' : '#4CAF50' }}>{o.status || 'Tamamlandı'}</span></td>
                          <td style={{ textAlign: 'right' }}>
                            <button className="settings-btn danger" style={{ padding: '4px 10px', fontSize: 11 }} onClick={() => handleDeletePastOrder(i)}>Sil</button>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
              {pastOrders.length > 0 && (
                <div style={{ marginTop: 15, textAlign: 'right' }}>
                  <button className="settings-btn danger" onClick={handleClearPastOrders}>Tüm Geçmişi Temizle</button>
                </div>
              )}
            </div>
          )}

          {activeTab === 'network' && (
            <div>
              <div className="settings-section-title">Sistem & Ağ Durumu</div>
              <div className="settings-card">
                <div className="settings-card-title">Bağlantı Bilgileri</div>
                <p style={{ color: '#ccc', marginBottom: 5 }}>Kasa programı şu anda aşağıdaki IP adresi üzerinden yayında. Garson cihazlarının bu IP adresine bağlı olduğundan emin olun.</p>
                <div style={{ display: 'flex', alignItems: 'center', fontSize: 24, fontWeight: 'bold', color: '#FF9800', margin: '15px 0' }}>
                  <span className="status-badge online"></span>
                  {networkStatus?.ip}:{networkStatus?.port}
                </div>
              </div>
              <div className="settings-card">
                <div className="settings-card-title">Aktif Garson Cihazları (App2)</div>
                {networkStatus?.connectedDevices?.length > 0 ? (
                  <ul style={{ paddingLeft: 20, color: '#4CAF50', fontWeight: 'bold' }}>
                    {networkStatus.connectedDevices.map((ip: string, i: number) => (
                      <li key={i} style={{ marginBottom: 5 }}>Cihaz: {ip}</li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ color: '#F44336' }}>Şu an hiçbir garson cihazı bağlı değil.</p>
                )}
                <button className="settings-btn" style={{ marginTop: 15 }} onClick={fetchNetworkStatus}>Yenile</button>
              </div>
            </div>
          )}

          {activeTab === 'printer' && (
            <div>
              <div className="settings-section-title">Yazıcı Ayarları</div>
              <div className="settings-card">
                <div className="settings-card-title">Mevcut Yazıcı: <span style={{ color: '#FF9800' }}>{settings.YAZICI_ADI || 'Seçilmedi'}</span></div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginTop: 15 }}>
                  {printers.map((p, i) => (
                    <button key={i} className="settings-btn" style={{ textAlign: 'left', padding: 15 }} onClick={() => selectPrinter(p.name)}>
                      🖨️ {p.name} {p.isDefault ? '(Varsayılan)' : ''}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'spotify' && (
            <div>
              <div className="settings-section-title">Spotify & API Ayarları</div>
              <div className="settings-card">
                <div className="settings-card-title">Spotify API Bilgileri</div>
                <label style={{ display: 'block', fontSize: 12, color: 'gray', marginBottom: 5 }}>Client ID</label>
                <input className="settings-input" value={settings.SPOTIFY_CLIENT_ID || ''} onChange={e => handleSettingChange('SPOTIFY_CLIENT_ID', e.target.value)} />
                
                <label style={{ display: 'block', fontSize: 12, color: 'gray', marginBottom: 5 }}>Client Secret</label>
                <input className="settings-input" value={settings.SPOTIFY_CLIENT_SECRET || ''} onChange={e => handleSettingChange('SPOTIFY_CLIENT_SECRET', e.target.value)} />
                
                <label style={{ display: 'block', fontSize: 12, color: 'gray', marginBottom: 5 }}>YouTube TV Linki</label>
                <input className="settings-input" value={settings.YOUTUBE_LINK || ''} onChange={e => handleSettingChange('YOUTUBE_LINK', e.target.value)} />
                
                <div className="settings-row" style={{ marginTop: 20 }}>
                  <button className="settings-btn primary" onClick={handleSaveSettings}>Değişiklikleri Kaydet</button>
                  <button className="settings-btn success" onClick={triggerSpotifyLogin}>Spotify'ı Yetkilendir (Login)</button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'updates' && (
            <div>
              <div className="settings-section-title">Uygulama Güncellemeleri</div>
              <div className="settings-card" style={{ textAlign: 'center', padding: 40 }}>
                <h2 style={{ color: '#4CAF50', fontSize: 24, marginBottom: 20 }}>
                  {isCheckingUpdate ? 'Kontrol ediliyor...' : (latestRelease ? `Yeni Versiyon: ${latestRelease.name || latestRelease.tag_name}` : 'Güncelleme bulunamadı veya henüz kontrol edilmedi.')}
                </h2>
                {latestRelease && !isCheckingUpdate && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 15, alignItems: 'center' }}>
                    {latestRelease.assets?.filter((a: any) => a.name.endsWith('.exe')).map((asset: any) => (
                      <button key={asset.id} className="settings-btn" onClick={() => window.open(asset.browser_download_url, '_blank')}>
                        Kasa EXE İndir ({asset.name})
                      </button>
                    ))}
                    {latestRelease.assets?.filter((a: any) => a.name.endsWith('.apk')).map((asset: any) => (
                      <div key={asset.id} className="settings-row" style={{ justifyContent: 'center' }}>
                        <button className="settings-btn" onClick={() => window.open(asset.browser_download_url, '_blank')}>
                          APK İndir
                        </button>
                        <button className="settings-btn primary" onClick={() => sendUpdateToPhones(asset.browser_download_url)}>
                          Garsonlara Otomatik Kurdur (Gönder)
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
