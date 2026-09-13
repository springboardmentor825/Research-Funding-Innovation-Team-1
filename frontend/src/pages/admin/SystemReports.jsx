import React, { useEffect, useState } from 'react'
import AppLayout from '../../components/layout/AppLayout'
import adminService from '../../services/admin'
import { BookOpen, Download, AlertTriangle, FileText, Calendar, Database, CheckCircle2 } from 'lucide-react'

function SystemReports() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchReports = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await adminService.getReports()
      setData(res)
    } catch (err) {
      console.error('System reports fetch error:', err)
      setError('Unable to load platform system reports directory.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchReports()
  }, [])

  const reports = data?.reports || []

  const handleExportReport = (reportId) => {
    const url = adminService.exportReportUrl(reportId)
    window.open(url, '_blank')
  }

  return (
    <AppLayout
      title="System Reports & Auditing"
      subtitle="Generate, review, and export platform system reports across key intelligence domains"
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>

        {loading ? (
          <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Building system reports directory...
          </div>
        ) : error ? (
          <div className="ai-card" style={{ padding: '3rem', textAlign: 'center', color: '#EF4444' }}>
            <AlertTriangle size={36} style={{ marginBottom: '0.75rem' }} />
            <h3>Unable to Load System Reports</h3>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>{error}</p>
            <button onClick={fetchReports} className="btn-ai-primary" style={{ padding: '0.5rem 1.25rem' }}>
              Retry
            </button>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
            {reports.map((rpt) => (
              <div 
                key={rpt.id}
                className="ai-card"
                style={{
                  padding: '1.5rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '1.25rem'
                }}
              >
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      padding: '0.2rem 0.6rem',
                      borderRadius: '12px',
                      background: 'rgba(6, 182, 212, 0.15)',
                      color: 'var(--accent-cyan-light)',
                      border: '1px solid rgba(6, 182, 212, 0.3)',
                      textTransform: 'uppercase'
                    }}>
                      {rpt.category}
                    </span>
                    <span style={{ fontSize: '0.775rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <Calendar size={13} /> {rpt.generated_date}
                    </span>
                  </div>

                  <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#F8FAFC', margin: 0, lineHeight: 1.3 }}>
                    {rpt.title}
                  </h3>

                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.45 }}>
                    {rpt.description}
                  </p>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                    <Database size={14} color="var(--accent-emerald)" />
                    <span><strong>{rpt.records_count}</strong> Database Records</span>
                  </div>
                </div>

                <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
                  <button
                    onClick={() => handleExportReport(rpt.id)}
                    className="btn-ai-primary"
                    style={{ padding: '0.5rem 1rem', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
                  >
                    <Download size={15} /> Export CSV
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </AppLayout>
  )
}

export default SystemReports
