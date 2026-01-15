import React, { useState } from 'react'
import '../App.css'

const PaymentModal = ({ product, onClose, onPaymentSuccess }) => {
    const [loading, setLoading] = useState(false)
    const [success, setSuccess] = useState(false)
    const [orderId, setOrderId] = useState('')

    const handlePay = () => {
        setLoading(true)
        setTimeout(() => {
            // Generate ID
            const newId = 'ORD-' + Math.floor(1000 + Math.random() * 9000)
            setOrderId(newId)

            // Notify Parent
            onPaymentSuccess({
                id: newId,
                item: product,
                date: new Date().toISOString(),
                status: 'Preparing for Shipment 📦'
            })

            setLoading(false)
            setSuccess(true)
        }, 2000)
    }

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" onClick={e => e.stopPropagation()}>
                <button className="modal-close" onClick={onClose}>×</button>

                <div className="payment-flow">
                    {success ? (
                        <div className="success-state" style={{ textAlign: 'center', padding: '2rem 0' }}>
                            <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🎉</div>
                            <h2 style={{ color: '#22c55e', marginBottom: '1rem' }}>Order Placed!</h2>
                            <p>Your Order ID is:</p>
                            <div style={{
                                background: 'var(--bg-input)',
                                padding: '1rem',
                                fontSize: '1.5rem',
                                fontWeight: 'bold',
                                borderRadius: '8px',
                                margin: '1rem 0',
                                letterSpacing: '2px',
                                border: '1px dashed var(--accent)'
                            }}>
                                {orderId}
                            </div>
                            <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
                                Use this ID to track your order status in the shop.
                            </p>
                            <button className="pay-button" onClick={onClose}>
                                Done
                            </button>
                        </div>
                    ) : !loading ? (
                        <>
                            <div className="payment-header">
                                <h2>Checkout</h2>
                                <p>Complete your purchase securely</p>
                            </div>

                            <div className="order-summary">
                                <img
                                    src={product.image}
                                    alt={product.name}
                                    onError={(e) => e.target.src = 'https://via.placeholder.com/300x200?text=🌸'}
                                />
                                <div className="summary-details">
                                    <h4>{product.name}</h4>
                                    <p className="shop-name">Sold by {product.shop_name || 'UCP Shop'}</p>
                                    <p className="summary-price">${product.price}</p>
                                </div>
                            </div>

                            {product.shipping_details && (
                                <div style={{
                                    background: 'var(--bg-card)',
                                    padding: '1rem',
                                    borderRadius: '8px',
                                    marginBottom: '1rem',
                                    border: '1px solid var(--accent)'
                                }}>
                                    <h5 style={{ margin: '0 0 8px 0', color: 'var(--accent)' }}>Shipping Details (Confident)</h5>
                                    <p style={{ margin: '0', color: 'var(--text-primary)' }}>{product.shipping_details.name}</p>
                                    <p style={{ margin: '0', color: 'var(--text-secondary)' }}>{product.shipping_details.address}</p>
                                </div>
                            )}

                            <div className="payment-form">
                                <div className="form-group">
                                    <label>Email Address</label>
                                    <input type="email" placeholder="you@example.com" />
                                </div>
                                <div className="form-group">
                                    <label>Card Details (Dummy)</label>
                                    <div className="card-input">
                                        <input type="text" placeholder="4242 4242 4242 4242" defaultValue="4242 4242 4242 4242" />
                                        <input type="text" placeholder="MM/YY" className="short" defaultValue="12/28" />
                                        <input type="text" placeholder="CVC" className="short" defaultValue="123" />
                                    </div>
                                </div>

                                <button className="pay-button" onClick={handlePay}>
                                    Pay ${product.price}
                                </button>
                                <p className="secure-badge">🔒 Encrypted Wrapper (Dummy)</p>
                            </div>
                        </>
                    ) : (
                        <div className="processing-state">
                            <div className="spinner"></div>
                            <h3>Processing Payment...</h3>
                            <p>Connecting to {product.shop_name || 'Merchant'}...</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default PaymentModal
