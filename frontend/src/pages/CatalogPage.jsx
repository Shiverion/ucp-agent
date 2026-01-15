import React from 'react'

const CatalogPage = ({ products, activeTab, setActiveTab, onProductSelect, categories, onTrackOrder }) => {
    const filteredProducts = products.filter(p =>
        activeTab === 'all' || p.category === activeTab
    )

    return (
        <div className="main-content">
            <header className="header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                    <h1>🌸 UCP Flower Shop</h1>
                    <p>AI-powered shopping with Universal Commerce Protocol</p>
                </div>
                <button
                    onClick={onTrackOrder}
                    className="track-button"
                    style={{
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border)',
                        color: 'var(--text-primary)',
                        padding: '8px 16px',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                    }}
                >
                    📦 Track Order
                </button>
            </header>

            <div className="catalog-section">
                <div className="tabs">
                    {categories.map(cat => (
                        <button
                            key={cat}
                            className={`tab ${activeTab === cat ? 'active' : ''}`}
                            onClick={() => setActiveTab(cat)}
                        >
                            {cat.charAt(0).toUpperCase() + cat.slice(1)}
                        </button>
                    ))}
                </div>

                <div className="products-grid">
                    {filteredProducts.map(product => (
                        <div
                            key={product.id}
                            className="product-card"
                            onClick={() => onProductSelect(product)}
                        >
                            <div className="product-image">
                                <span className="shop-badge">
                                    {product.shop_name || 'UCP Shop'}
                                </span>
                                <img
                                    src={product.image}
                                    alt={product.name}
                                    onError={(e) => e.target.src = 'https://via.placeholder.com/300x200?text=🌸'}
                                />
                            </div>
                            <div className="product-info">
                                <h4>{product.name}</h4>
                                <p className="description">{product.description}</p>
                                <p className="price">${product.price}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default CatalogPage
