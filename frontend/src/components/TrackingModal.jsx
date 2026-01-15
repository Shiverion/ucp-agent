import React, { useState, useEffect } from 'react'

const TrackingModal = ({ onClose, orders, initialOrderId }) => {
    const [orderId, setOrderId] = useState(initialOrderId || '')
    const [result, setResult] = useState(null)
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    // Auto-track if ID provided
    useEffect(() => {
        if (initialOrderId) {
            handleTrack(initialOrderId)
        }
    }, [])

    const handleTrack = (idOverride) => {
        const idToSearch = typeof idOverride === 'string' ? idOverride : orderId
        if (!idToSearch || !idToSearch.trim()) return

        setLoading(true)
        setError('')
        setResult(null)

        // Simulate network lookup
        setTimeout(() => {
            const found = orders.find(o => o.id.toLowerCase() === idToSearch.trim().toLowerCase())

            if (found) {
                setResult(found)
            } else {
                setError(`Order #${idToSearch} not found. Please checks your ID.`)
            }
            setLoading(false)
        }, 800)
    }

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: '500px' }}>
                <button className="modal-close" onClick={onClose}>×</button>

                <div className="tracking-flow" style={{ padding: '2rem', width: '100%', color: 'white' }}>
                    <div className="payment-header">
                        <h2>📦 Track Your Order</h2>
                        <p>Enter your Order ID to see the status</p>
                    </div>

                    <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                        <input
                            type="text"
                            placeholder="e.g. ORD-8821"
                            value={orderId}
                            onChange={(e) => setOrderId(e.target.value)}
                            style={{ textAlign: 'center', fontSize: '1.2rem' }}
                        />
                    </div>

                    {!result && !loading && (
                        <button className="pay-button" onClick={() => handleTrack()}>
                            Track Order
                        </button>
                    )}

                    {loading && (
                        <div className="loading" style={{ justifyContent: 'center' }}>
                            <span></span><span></span><span></span>
                        </div>
                    )}

                    {error && (
                        <div style={{ color: '#ef4444', textAlign: 'center', marginTop: '1rem', padding: '10px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px' }}>
                            {error}
                        </div>
                    )}

                    {result && (
                        <div className="tracking-result" style={{ marginTop: '0rem', animation: 'fadeIn 0.3s ease' }}>
                            <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
                                <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>🚚</div>
                                <h3 style={{ color: '#22c55e' }}>On the way!</h3>
                                <p style={{ color: '#94a3b8' }}>Estimated Delivery: Tomorrow</p>
                            </div>

                            <div className="order-summary" style={{ marginBottom: '1rem' }}>
                                <img src={result.item.image} alt={result.item.name} />
                                <div className="summary-details">
                                    <h4>{result.item.name}</h4>
                                    <p className="shop-name">{result.id}</p>
                                    <p className="summary-price">${result.item.price}</p>
                                </div>
                            </div>

                            <div style={{ background: '#0f172a', padding: '1rem', borderRadius: '8px' }}>
                                <p style={{ marginBottom: '8px' }}><strong>Status:</strong> Shipped</p>
                                <p><strong>Tracking:</strong> UH-72819283-US</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default TrackingModal
