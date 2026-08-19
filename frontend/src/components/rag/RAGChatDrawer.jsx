import React, { useState, useRef, useEffect } from 'react'
import ragService from '../../services/rag'
import { Bot, Send, X, Sparkles, User, FileText, RefreshCw, ChevronDown, ExternalLink } from 'lucide-react'

function RAGChatDrawer({ isOpen, onClose }) {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState(() => {
    try {
      const saved = sessionStorage.getItem('rag_chat_messages')
      return saved ? JSON.parse(saved) : [
        {
          sender: 'bot',
          text: 'Hello! I am your AI Research Assistant. Ask me anything about funding schemes, research papers, patents, or RAG architecture.'
        }
      ]
    } catch {
      return [
        {
          sender: 'bot',
          text: 'Hello! I am your AI Research Assistant. Ask me anything about funding schemes, research papers, patents, or RAG architecture.'
        }
      ]
    }
  })

  const [loading, setLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState(null)
  const messagesEndRef = useRef(null)

  const quickPrompts = [
    "What funding opportunities are available?",
    "Show research papers on AI & funding",
    "List registered patents and assignees",
    "What is Retrieval Augmented Generation?",
    "Who won IPL 2025?"
  ]

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    try {
      sessionStorage.setItem('rag_chat_messages', JSON.stringify(messages))
    } catch (e) {
      console.warn('Could not save session chat messages:', e)
    }
    if (isOpen) {
      scrollToBottom()
    }
  }, [messages, isOpen])

  const sendQuery = async (userText) => {
    if (!userText.trim() || loading) return

    setQuery('')
    setErrorMsg(null)
    setMessages(prev => [...prev, { sender: 'user', text: userText }])
    setLoading(true)

    try {
      const data = await ragService.chat(userText)
      setMessages(prev => [
        ...prev, 
        { 
          sender: 'bot', 
          text: data.answer || 'No text response generated.',
          sources: data.sources || []
        }
      ])
    } catch (err) {
      console.error('RAG Chat error:', err)
      setErrorMsg('Network or service error. Please verify backend FastAPI server is active.')
      setMessages(prev => [
        ...prev, 
        { 
          sender: 'bot', 
          text: 'Apologies, I encountered an issue querying the RAG intelligence system. Click Retry below to resend your query.',
          isError: true,
          failedQuery: userText
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleSend = (e) => {
    e.preventDefault()
    sendQuery(query)
  }

  if (!isOpen) return null

  return (
    <div style={{
      position: 'fixed',
      right: '20px',
      bottom: '20px',
      width: '450px',
      height: '630px',
      maxWidth: 'calc(100vw - 30px)',
      maxHeight: 'calc(100vh - 30px)',
      backgroundColor: '#0B132B',
      border: '1px solid var(--border-glow)',
      borderRadius: '18px',
      boxShadow: '0 20px 50px rgba(0, 0, 0, 0.8), 0 0 35px rgba(6, 182, 212, 0.3)',
      display: 'flex',
      flexDirection: 'column',
      zIndex: 1000,
      overflow: 'hidden'
    }}>
      {/* Drawer Header */}
      <div style={{
        padding: '0.85rem 1.1rem',
        background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%)',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '34px',
            height: '34px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, var(--accent-cyan) 0%, #0284C7 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 12px rgba(6, 182, 212, 0.5)'
          }}>
            <Bot size={20} color="#FFFFFF" />
          </div>
          <div>
            <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#F8FAFC' }}>
              AI RAG Assistant
            </div>
            <div style={{ fontSize: '0.725rem', color: 'var(--accent-cyan-light)', fontWeight: 600 }}>
              Hybrid RAG • Vector & MySQL DB Active
            </div>
          </div>
        </div>

        <button 
          onClick={onClose}
          style={{ background: 'none', border: 'none', color: '#94A3B8', cursor: 'pointer', padding: '0.25rem', borderRadius: '6px' }}
        >
          <X size={20} />
        </button>
      </div>

      {/* Messages List */}
      <div style={{ flexGrow: 1, padding: '1rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
        {messages.map((msg, idx) => (
          <div 
            key={idx} 
            style={{ 
              display: 'flex', 
              gap: '0.65rem',
              alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '90%'
            }}
          >
            {msg.sender === 'bot' && (
              <div style={{
                width: '28px',
                height: '28px',
                borderRadius: '8px',
                background: 'rgba(6, 182, 212, 0.2)',
                border: '1px solid rgba(6, 182, 212, 0.4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}>
                <Sparkles size={14} color="var(--accent-cyan-light)" />
              </div>
            )}

            <div style={{
              padding: '0.75rem 1rem',
              borderRadius: msg.sender === 'user' ? '14px 14px 2px 14px' : '14px 14px 14px 2px',
              background: msg.sender === 'user' 
                ? 'linear-gradient(135deg, var(--accent-cyan) 0%, #0284C7 100%)' 
                : 'rgba(30, 41, 59, 0.85)',
              border: msg.sender === 'bot' ? '1px solid var(--border-color)' : 'none',
              color: '#F8FAFC',
              fontSize: '0.85rem',
              lineHeight: '1.5',
              whiteSpace: 'pre-wrap'
            }}>
              <div>{msg.text}</div>
              
              {/* Context Sources Badges */}
              {msg.sources && msg.sources.length > 0 && (
                <div style={{ marginTop: '0.65rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)', fontSize: '0.725rem' }}>
                  <div style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.35rem', color: 'var(--accent-cyan-light)' }}>
                    <FileText size={12} /> Sources ({msg.sources.length}):
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                    {msg.sources.map((src, sIdx) => (
                      <span key={sIdx} style={{
                        background: 'rgba(6, 182, 212, 0.15)',
                        border: '1px solid rgba(6, 182, 212, 0.3)',
                        color: 'var(--accent-cyan-light)',
                        padding: '0.2rem 0.5rem',
                        borderRadius: '6px',
                        fontSize: '0.7rem'
                      }}>
                        [{src.type || 'DB Record'}] {src.title || src.name || 'Source Record'}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Retry button on error */}
              {msg.isError && msg.failedQuery && (
                <button
                  onClick={() => sendQuery(msg.failedQuery)}
                  style={{
                    marginTop: '0.5rem',
                    background: 'rgba(239, 68, 68, 0.2)',
                    border: '1px solid #EF4444',
                    color: '#EF4444',
                    padding: '0.3rem 0.65rem',
                    borderRadius: '6px',
                    fontSize: '0.75rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.35rem'
                  }}
                >
                  <RefreshCw size={12} /> Retry Query
                </button>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', color: 'var(--accent-cyan-light)', fontSize: '0.825rem', paddingLeft: '2rem' }}>
            <Sparkles size={14} style={{ animation: 'spin 2s linear infinite' }} /> 
            Retrieving RAG passages & synthesizing response...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Suggestion Chips */}
      {!loading && (
        <div style={{ padding: '0 1rem 0.5rem 1rem', display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
          {quickPrompts.slice(0, 4).map((prompt, pIdx) => (
            <button
              key={pIdx}
              onClick={() => sendQuery(prompt)}
              style={{
                background: 'rgba(6, 182, 212, 0.1)',
                border: '1px solid rgba(6, 182, 212, 0.25)',
                color: 'var(--accent-cyan-light)',
                borderRadius: '20px',
                padding: '0.25rem 0.6rem',
                fontSize: '0.725rem',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                whiteSpace: 'nowrap'
              }}
            >
              💡 {prompt}
            </button>
          ))}
        </div>
      )}

      {/* Input Footer */}
      <form onSubmit={handleSend} style={{ padding: '0.85rem 1rem', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '0.5rem', background: '#080C14' }}>
        <input 
          type="text"
          placeholder="Ask RAG assistant about funding, papers, patents..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="ai-input"
          style={{ fontSize: '0.85rem', height: '40px' }}
        />
        <button 
          type="submit" 
          disabled={loading || !query.trim()}
          className="btn-ai-primary"
          style={{ padding: '0 1rem', height: '40px', borderRadius: '10px' }}
        >
          <Send size={16} />
        </button>
      </form>
    </div>
  )
}

export default RAGChatDrawer
