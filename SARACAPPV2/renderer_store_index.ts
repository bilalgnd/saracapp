import { create } from 'zustand'

export interface OrderItem {
  name: string
  portion: string
  price: number
  notes: string
}

export interface Order {
  customer_name: string
  time: string
  items: OrderItem[]
  total_amount: number
  status: 'waiting' | 'prepared' | 'served' | 'Tamamlandı' | 'İptal'
  color?: string
  order_note?: string
  completedAt?: string
}

interface AppState {
  orders: Order[]
  menu: any
  cart: OrderItem[]
  editingOrderIndex: number | null
  isSettingsMode: boolean
  activeTab: number
  orderSequence: number
  
  setOrders: (orders: Order[]) => void
  setMenu: (menu: any) => void
  setCart: (items: OrderItem[]) => void
  addToCart: (item: OrderItem) => void
  removeFromCart: (index: number) => void
  clearCart: () => void
  setEditingOrder: (index: number | null) => void
  setSettingsMode: (mode: boolean) => void
  setActiveTab: (tabIndex: number) => void
  incrementOrderSequence: () => void
}

export const useStore = create<AppState>((set) => ({
  orders: [],
  menu: null,
  cart: [],
  editingOrderIndex: null,
  isSettingsMode: false,
  activeTab: 0,
  orderSequence: 1,
  
  setOrders: (orders) => set({ orders }),
  setMenu: (menu) => set({ menu }),
  setCart: (items) => set({ cart: items }),
  addToCart: (item) => set((state) => ({ cart: [...state.cart, item] })),
  removeFromCart: (index) => set((state) => ({ cart: state.cart.filter((_, i) => i !== index) })),
  clearCart: () => set({ cart: [], editingOrderIndex: null }),
  setEditingOrder: (index) => set({ editingOrderIndex: index }),
  setSettingsMode: (mode) => set({ isSettingsMode: mode }),
  setActiveTab: (tabIndex) => set({ activeTab: tabIndex }),
  incrementOrderSequence: () => set((state) => ({ orderSequence: state.orderSequence + 1 }))
}))
