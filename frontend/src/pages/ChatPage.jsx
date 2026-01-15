import React, { useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import FormattedMessage from '../components/FormattedMessage'
import { Link } from 'react-router-dom'

const ChatPage = ({ messages, loading, input, setInput, sendMessage, onBuy, getOrderStatus, onTrackOrder }) => {
    const messagesEndRef = useRef(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            sendMessage()
        }
    }

    return (
        <div className="chat-page container" style={{ maxWidth: '900px', margin: '0 auto', height: '100vh', display: 'flex', flexDirection: 'column' }}>
            <div className="chat-header-row">
                <h3 className="chat-header-title">💬 AI Assistant</h3>
                <Link to="/" className="close-chat-btn" style={{ textDecoration: 'none', color: 'inherit' }}>
                    🏠 Home
                </Link>
            </div>

            <div className="messages" style={{ flex: 1 }}>
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.role}`}>
                        <div className="message-avatar">
                            {msg.role === 'assistant' ? '🤖' : '👤'}
                        </div>
                        <div className="message-content">
                            {msg.role === 'assistant' ? (
                                <FormattedMessage
                                    content={msg.content}
                                    onBuy={onBuy}
                                    getOrderStatus={getOrderStatus}
                                    onTrackOrder={onTrackOrder}
                                />
                            ) : (
                                <ReactMarkdown>{msg.content}</ReactMarkdown>
                            )}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="message assistant">
                        <div className="message-avatar">🤖</div>
                        <div className="loading">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="input-area">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask about flowers..."
                    disabled={loading}
                />
                <button onClick={sendMessage} disabled={loading || !input.trim()}>
                    Send
                </button>
            </div>
        </div>
    )
}

export default ChatPage
