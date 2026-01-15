import { useState, check, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import './App.css'

// Pages & Components
import CatalogPage from './pages/CatalogPage'
import ChatPage from './pages/ChatPage'
import PaymentModal from './components/PaymentModal'
import TrackingModal from './components/TrackingModal'

const API_URL = 'http://localhost:8183'

// Floating Chat Button Component
const ChatButton = () => {
  const location = useLocation()
  // Only show on home page
  if (location.pathname !== '/') return null

  return (
    <Link to="/chat" className="floating-chat-btn">
      💬
    </Link>
  )
}

function App() {
  console.log("DEBUG: App component rendered (Router)")

  // --- Global State ---
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "🌸 **Welcome to the UCP Flower Shop!** I'm your AI shopping assistant.\n\nBrowse our collection below or ask me anything!"
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [products, setProducts] = useState([])
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [activeTab, setActiveTab] = useState('all')

  // Tracking State
  const [dummyOrders, setDummyOrders] = useState([])
  const [isTrackingOpen, setIsTrackingOpen] = useState(false)
  const [trackingInitialId, setTrackingInitialId] = useState(null)

  // Fetch products on mount
  useEffect(() => {
    fetch(`${API_URL}/products`)
      .then(res => res.json())
      .then(data => setProducts(data))
      .catch(err => console.error('Failed to load products:', err))
  }, [])

  const handleOrderSuccess = (order) => {
    console.log("New Order:", order)
    setDummyOrders(prev => [order, ...prev])
  }

  const getOrderStatus = (id) => {
    return dummyOrders.find(o => o.id.toLowerCase() === id.toLowerCase()) || null
  }

  // Chat Logic
  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
      })

      if (!response.ok) throw new Error('Failed to get response')

      const data = await response.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "I'm sorry, I encountered an error. Please try again."
      }])
    } finally {
      setLoading(false)
    }
  }

  // Buy Logic (Opens Modal from Chat)
  const handleBuyChat = (product) => {
    // Open modal directly
    setSelectedProduct(product)
  }

  // Categories
  const categories = ['all', 'flowers', 'plants', 'arrangements']

  return (
    <Router>
      <div className="app-container">
        <Routes>
          <Route
            path="/"
            element={
              <CatalogPage
                products={products}
                activeTab={activeTab}
                setActiveTab={setActiveTab}
                categories={categories}
                onProductSelect={setSelectedProduct}
                onTrackOrder={() => setIsTrackingOpen(true)}
              />
            }
          />
          <Route
            path="/chat"
            element={
              <ChatPage
                messages={messages}
                loading={loading}
                input={input}
                setInput={setInput}
                sendMessage={sendMessage}
                onBuy={handleBuyChat}
                getOrderStatus={getOrderStatus}
                onTrackOrder={(id) => {
                  setTrackingInitialId(typeof id === 'string' ? id : null)
                  setIsTrackingOpen(true)
                }}
              />
            }
          />
        </Routes>

        {/* Global Elements */}
        {/* Only show floating chat button on home, but handled by component inside Router context */}
        <ChatButton />

        {selectedProduct && (
          <PaymentModal
            product={selectedProduct}
            onClose={() => setSelectedProduct(null)}
            onPaymentSuccess={handleOrderSuccess}
          />
        )}

        {isTrackingOpen && (
          <TrackingModal
            onClose={() => {
              setIsTrackingOpen(false)
              setTrackingInitialId(null)
            }}
            orders={dummyOrders}
            initialOrderId={trackingInitialId}
          />
        )}
      </div>
    </Router>
  )
}

export default App
