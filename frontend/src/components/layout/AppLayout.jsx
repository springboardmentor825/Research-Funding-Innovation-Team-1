import React, { useState } from 'react'
import Sidebar from './Sidebar'
import Header from './Header'
import RAGChatDrawer from '../rag/RAGChatDrawer'
import { Bot, Sparkles } from 'lucide-react'

function AppLayout({ children, title, subtitle, searchValue, onSearchChange }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [ragOpen, setRagOpen] = useState(false)

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--bg-dark)' }}>
      {/* Fixed Sidebar */}
      <Sidebar mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} />

      {/* Main Content Body */}
      <div 
        style={{ 
          flexGrow: 1, 
          display: 'flex', 
          flexDirection: 'column', 
          minWidth: 0,
          marginLeft: '260px', // matches sidebar width
          transition: 'margin-left 0.3s ease'
        }}
        className="main-content-layout"
      >
        <Header 
          title={title} 
          subtitle={subtitle} 
          searchValue={searchValue}
          onSearchChange={onSearchChange}
          setMobileOpen={setMobileOpen}
        />

        <main style={{ padding: '2rem', flexGrow: 1, maxWidth: '1400px', width: '100%', margin: '0 auto' }}>
          {children}
        </main>
      </div>

      {/* Floating RAG Assistant Toggle Button */}
      {!ragOpen && (
        <button
          onClick={() => setRagOpen(true)}
          style={{
            position: 'fixed',
            right: '24px',
            bottom: '24px',
            padding: '0.85rem 1.35rem',
            borderRadius: '9999px',
            background: 'linear-gradient(135deg, var(--accent-cyan) 0%, #0284C7 100%)',
            color: '#FFFFFF',
            border: 'none',
            fontWeight: 700,
            fontSize: '0.9rem',
            cursor: 'pointer',
            boxShadow: '0 10px 25px rgba(6, 182, 212, 0.4), 0 0 15px rgba(6, 182, 212, 0.3)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.65rem',
            zIndex: 90,
            transition: 'all 0.2s ease'
          }}
          className="glow-animation"
        >
          <Bot size={20} />
          <span>Ask AI Assistant</span>
        </button>
      )}

      {/* RAG Chat Assistant Drawer */}
      <RAGChatDrawer isOpen={ragOpen} onClose={() => setRagOpen(false)} />
    </div>
  )
}

export default AppLayout
