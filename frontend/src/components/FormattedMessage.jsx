import React from 'react'
import ReactMarkdown from 'react-markdown'

const FormattedMessage = ({ content, onBuy, getOrderStatus, onTrackOrder }) => {
    const jsonRegex = /```(?:json)?\s*([\s\S]*?)\s*```/i
    const match = content.match(jsonRegex)

    let products = []
    let textContent = content

    if (match) {
        try {
            const jsonStr = match[1].trim()
            if (jsonStr.startsWith('[') && jsonStr.endsWith(']')) {
                products = JSON.parse(jsonStr)
                textContent = content.replace(match[0], '')
            }
        } catch (e) {
            console.warn("Failed to parse product JSON:", e)
        }
    }

    return (
        <div>
            <ReactMarkdown>{textContent}</ReactMarkdown>
            {products.length > 0 && (
                <div className="chat-products-grid">
                    {products.map((p, i) => {
                        // Special Handling for Tracking Action
                        if (p.action === 'track_order' && getOrderStatus) {
                            const order = getOrderStatus(p.order_id)
                            if (order) {
                                return (
                                    <div
                                        key={i}
                                        className="chat-product-card"
                                        onClick={() => onTrackOrder(order.id)}
                                        style={{ border: '1px solid var(--accent)', cursor: 'pointer' }}
                                    >
                                        <div className="chat-product-image">
                                            <img src={order.item.image} alt={order.item.name} />
                                        </div>
                                        <div className="chat-product-details">
                                            <h5 style={{ color: 'var(--accent)' }}>Order Found! (Click to View)</h5>
                                            <p className="chat-product-shop">ID: {order.id}</p>
                                            <p className="chat-product-price" style={{ fontSize: '0.9rem' }}>{order.status}</p>
                                        </div>
                                    </div>
                                )
                            } else {
                                return (
                                    <div key={i} className="chat-product-card" style={{ opacity: 0.7 }}>
                                        <div className="chat-product-details">
                                            <h5>Order Not Found</h5>
                                            <p className="chat-product-shop">ID: {p.order_id}</p>
                                            <p style={{ fontSize: '0.8rem', color: '#ef4444' }}>We couldn't find this order.</p>
                                        </div>
                                    </div>
                                )
                            }
                        }

                        return (
                            <div key={i} className="chat-product-card">
                                <div className="chat-product-image">
                                    <img
                                        src={p.image}
                                        alt={p.name}
                                        onError={(e) => e.target.src = 'https://via.placeholder.com/150?text=🌸'}
                                    />
                                </div>
                                <div className="chat-product-details">
                                    <h5>{p.name}</h5>
                                    <p className="chat-product-shop">{p.shop_name}</p>
                                    <div className="chat-product-footer">
                                        <span className="chat-product-price">${p.price}</span>
                                        <button
                                            onClick={() => onBuy(p)}
                                            className={p.action === 'checkout' ? 'proceed-btn' : 'buy-btn'}
                                            style={{
                                                background: p.action === 'checkout' ? 'var(--accent)' : 'var(--primary)',
                                                color: 'white',
                                                border: 'none',
                                                padding: '6px 12px',
                                                borderRadius: '6px',
                                                cursor: 'pointer'
                                            }}
                                        >
                                            {p.action === 'checkout' ? 'Proceed to Payment' : 'Buy Now'}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )
                    })}
                </div>
            )}
        </div>
    )
}

export default FormattedMessage
