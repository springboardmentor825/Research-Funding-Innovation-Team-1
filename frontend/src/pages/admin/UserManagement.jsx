import React, { useEffect, useState } from 'react'
import AppLayout from '../../components/layout/AppLayout'
import adminService from '../../services/admin'
import { Users, Search, Filter, Shield, AlertTriangle, Check, Eye, Edit3, X, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react'

function UserManagement() {
  const [users, setUsers] = useState([])
  const [pagination, setPagination] = useState({ total: 0, page: 1, limit: 10, pages: 1 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Filters
  const [searchQuery, setSearchQuery] = useState('')
  const [roleFilter, setRoleFilter] = useState('all')

  // Modals state
  const [selectedUser, setSelectedUser] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [userModalOpen, setUserModalOpen] = useState(false)

  const [roleEditUser, setRoleEditUser] = useState(null)
  const [newRole, setNewRole] = useState('researcher')
  const [roleModalOpen, setRoleModalOpen] = useState(false)
  const [roleUpdateLoading, setRoleUpdateLoading] = useState(false)
  const [roleUpdateError, setRoleUpdateError] = useState(null)
  const [roleUpdateSuccess, setRoleUpdateSuccess] = useState(null)

  const fetchUsers = async (page = 1) => {
    setLoading(true)
    setError(null)
    try {
      const data = await adminService.getUsers({
        query: searchQuery,
        role: roleFilter,
        page: page,
        limit: 10
      })
      setUsers(data.users || [])
      setPagination(data.pagination || { total: 0, page: 1, limit: 10, pages: 1 })
    } catch (err) {
      console.error('Fetch users error:', err)
      setError('Unable to retrieve users list. Please check backend connection.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers(1)
  }, [roleFilter])

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    fetchUsers(1)
  }

  const handleOpenDetailModal = async (u) => {
    setUserModalOpen(true)
    setDetailLoading(true)
    setSelectedUser(null)
    try {
      const res = await adminService.getUserDetails(u.id)
      setSelectedUser(res)
    } catch (err) {
      console.error('Fetch user detail error:', err)
    } finally {
      setDetailLoading(false)
    }
  }

  const handleOpenRoleModal = (u) => {
    setRoleEditUser(u)
    setNewRole(u.role || 'researcher')
    setRoleUpdateError(null)
    setRoleUpdateSuccess(null)
    setRoleModalOpen(true)
  }

  const handleSaveRoleChange = async () => {
    if (!roleEditUser) return
    setRoleUpdateLoading(true)
    setRoleUpdateError(null)
    setRoleUpdateSuccess(null)
    try {
      const res = await adminService.updateUserRole(roleEditUser.id, newRole)
      setRoleUpdateSuccess(res.message || 'Role updated successfully.')
      fetchUsers(pagination.page)
      setTimeout(() => {
        setRoleModalOpen(false)
      }, 1500)
    } catch (err) {
      const errMsg = err.response?.data?.detail || 'Failed to update user role.'
      setRoleUpdateError(errMsg)
    } finally {
      setRoleUpdateLoading(false)
    }
  }

  return (
    <AppLayout
      title="User Account Management"
      subtitle="View, search, audit profiles, and manage system access roles"
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

        {/* Filter and Search Bar */}
        <div 
          className="ai-card"
          style={{
            padding: '1.25rem 1.5rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1rem'
          }}
        >
          {/* Role Filter Tabs */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
            {[
              { id: 'all', label: 'All Users' },
              { id: 'researcher', label: 'Researchers' },
              { id: 'startup_founder', label: 'Startup Founders' },
              { id: 'administrator', label: 'Administrators' }
            ].map((tab) => {
              const active = roleFilter === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setRoleFilter(tab.id)}
                  style={{
                    padding: '0.45rem 0.9rem',
                    borderRadius: '8px',
                    fontSize: '0.825rem',
                    fontWeight: active ? 700 : 500,
                    color: active ? '#F8FAFC' : 'var(--text-secondary)',
                    backgroundColor: active ? 'rgba(6, 182, 212, 0.2)' : 'rgba(30, 41, 59, 0.5)',
                    border: active ? '1px solid var(--accent-cyan)' : '1px solid var(--border-color)',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                >
                  {tab.label}
                </button>
              )
            })}
          </div>

          {/* Search Form */}
          <form onSubmit={handleSearchSubmit} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ position: 'relative' }}>
              <input
                type="text"
                placeholder="Search name or email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  padding: '0.5rem 0.85rem 0.5rem 2.25rem',
                  borderRadius: '8px',
                  backgroundColor: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-color)',
                  color: '#F8FAFC',
                  fontSize: '0.85rem',
                  width: '240px'
                }}
              />
              <Search size={15} color="var(--text-muted)" style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)' }} />
            </div>
            <button type="submit" className="btn-ai-primary" style={{ padding: '0.5rem 0.9rem', fontSize: '0.85rem' }}>
              Search
            </button>
          </form>
        </div>

        {/* Users Table Card */}
        <div className="ai-card" style={{ padding: '1.5rem' }}>

          {loading ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              Loading user registry...
            </div>
          ) : error ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: '#EF4444' }}>
              <AlertTriangle size={30} style={{ marginBottom: '0.5rem' }} />
              <div>{error}</div>
              <button onClick={() => fetchUsers(pagination.page)} className="btn-ai-primary" style={{ marginTop: '1rem', padding: '0.45rem 1rem' }}>
                Retry
              </button>
            </div>
          ) : users.length === 0 ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              No user accounts found matching your filter criteria.
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)', textAlign: 'left' }}>
                    <th style={{ padding: '0.75rem 1rem' }}>User</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Email</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Canonical Role</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Organization</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                    <th style={{ padding: '0.75rem 1rem' }}>Registered</th>
                    <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id} style={{ borderBottom: '1px solid rgba(30, 41, 59, 0.6)' }}>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <div style={{ fontWeight: 600, color: '#F8FAFC' }}>{u.full_name}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>ID: #{u.id}</div>
                      </td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)' }}>{u.email}</td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span style={{
                          fontSize: '0.75rem',
                          padding: '0.2rem 0.65rem',
                          borderRadius: '12px',
                          fontWeight: 700,
                          background: u.role === 'administrator' ? 'rgba(168, 85, 247, 0.2)' : u.role === 'startup_founder' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(6, 182, 212, 0.2)',
                          color: u.role === 'administrator' ? '#C084FC' : u.role === 'startup_founder' ? '#10B981' : 'var(--accent-cyan-light)',
                          border: u.role === 'administrator' ? '1px solid rgba(168, 85, 247, 0.4)' : '1px solid transparent'
                        }}>
                          {u.role}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-secondary)' }}>
                        {u.organization || 'N/A'}
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span style={{
                          fontSize: '0.725rem',
                          fontWeight: 700,
                          padding: '0.15rem 0.5rem',
                          borderRadius: '9999px',
                          background: u.account_status === 'active' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                          color: u.account_status === 'active' ? 'var(--accent-emerald)' : '#EF4444',
                          textTransform: 'uppercase'
                        }}>
                          {u.account_status}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)' }}>{u.created_at}</td>
                      <td style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.5rem' }}>
                          <button
                            onClick={() => handleOpenDetailModal(u)}
                            style={{ background: 'rgba(6, 182, 212, 0.1)', border: '1px solid rgba(6, 182, 212, 0.3)', color: 'var(--accent-cyan-light)', borderRadius: '6px', padding: '0.35rem 0.65rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.775rem' }}
                          >
                            <Eye size={14} /> Details
                          </button>
                          <button
                            onClick={() => handleOpenRoleModal(u)}
                            style={{ background: 'rgba(168, 85, 247, 0.1)', border: '1px solid rgba(168, 85, 247, 0.3)', color: '#C084FC', borderRadius: '6px', padding: '0.35rem 0.65rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.775rem' }}
                          >
                            <Edit3 size={14} /> Role
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination Controls */}
          {!loading && !error && pagination.pages > 1 && (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                Showing page {pagination.page} of {pagination.pages} ({pagination.total} total users)
              </span>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  disabled={pagination.page <= 1}
                  onClick={() => fetchUsers(pagination.page - 1)}
                  style={{ opacity: pagination.page <= 1 ? 0.5 : 1, padding: '0.4rem 0.75rem', borderRadius: '6px', background: 'rgba(30, 41, 59, 0.6)', border: '1px solid var(--border-color)', color: '#F8FAFC', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.8rem' }}
                >
                  <ChevronLeft size={15} /> Prev
                </button>
                <button
                  disabled={pagination.page >= pagination.pages}
                  onClick={() => fetchUsers(pagination.page + 1)}
                  style={{ opacity: pagination.page >= pagination.pages ? 0.5 : 1, padding: '0.4rem 0.75rem', borderRadius: '6px', background: 'rgba(30, 41, 59, 0.6)', border: '1px solid var(--border-color)', color: '#F8FAFC', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.8rem' }}
                >
                  Next <ChevronRight size={15} />
                </button>
              </div>
            </div>
          )}

        </div>

      </div>

      {/* USER DETAILS MODAL */}
      {userModalOpen && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(8, 12, 20, 0.85)', backdropFilter: 'blur(4px)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem' }}>
          <div className="ai-card" style={{ width: '100%', maxWidth: '650px', maxHeight: '85vh', overflowY: 'auto', padding: '1.75rem', position: 'relative' }}>
            <button
              onClick={() => setUserModalOpen(false)}
              style={{ position: 'absolute', right: '1.25rem', top: '1.25rem', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
            >
              <X size={20} />
            </button>

            {detailLoading || !selectedUser ? (
              <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                Loading profile audit details...
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
                  <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--accent-cyan) 0%, #0284C7 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, color: '#FFF', fontSize: '1.25rem' }}>
                    {selectedUser.user.full_name?.charAt(0) || 'U'}
                  </div>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.2rem', color: '#F8FAFC' }}>{selectedUser.user.full_name}</h3>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{selectedUser.user.email}</div>
                  </div>
                </div>

                {/* Account Details Table */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.85rem' }}>
                  <div>
                    <span style={{ color: 'var(--text-muted)', display: 'block' }}>Canonical Role:</span>
                    <strong style={{ color: 'var(--accent-cyan-light)' }}>{selectedUser.user.role}</strong>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-muted)', display: 'block' }}>Account Status:</span>
                    <strong style={{ color: 'var(--accent-emerald)' }}>{selectedUser.user.account_status}</strong>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-muted)', display: 'block' }}>Auth Provider:</span>
                    <span style={{ color: '#F8FAFC' }}>{selectedUser.user.auth_provider}</span>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-muted)', display: 'block' }}>Registered Date:</span>
                    <span style={{ color: '#F8FAFC' }}>{selectedUser.user.created_at}</span>
                  </div>
                </div>

                {/* Profile Breakdown */}
                {selectedUser.profile ? (
                  <div style={{ padding: '1rem', borderRadius: '10px', background: 'rgba(30, 41, 59, 0.5)', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem' }}>
                    <div style={{ fontWeight: 700, color: '#F8FAFC' }}>Research Profile</div>
                    <div><strong>Organization:</strong> {selectedUser.profile.organization}</div>
                    <div><strong>Designation:</strong> {selectedUser.profile.designation}</div>
                    <div><strong>Domain:</strong> {selectedUser.profile.research_domain}</div>
                    <div><strong>Technology Area:</strong> {selectedUser.profile.technology_area}</div>
                  </div>
                ) : (
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>No research profile attached.</div>
                )}

                {/* Activity Counts */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.75rem', textAlign: 'center' }}>
                  <div style={{ padding: '0.75rem', background: 'rgba(30, 41, 59, 0.6)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#F8FAFC' }}>{selectedUser.publications_summary?.count || 0}</div>
                    <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>Publications</div>
                  </div>
                  <div style={{ padding: '0.75rem', background: 'rgba(30, 41, 59, 0.6)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#F8FAFC' }}>{selectedUser.patents_summary?.count || 0}</div>
                    <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>Patents</div>
                  </div>
                  <div style={{ padding: '0.75rem', background: 'rgba(30, 41, 59, 0.6)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#F8FAFC' }}>{selectedUser.activity_summary?.total_recommendations_received || 0}</div>
                    <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>Recommendations</div>
                  </div>
                </div>

              </div>
            )}
          </div>
        </div>
      )}

      {/* ROLE MODIFICATION MODAL WITH LAST ADMIN PROTECTION */}
      {roleModalOpen && roleEditUser && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(8, 12, 20, 0.85)', backdropFilter: 'blur(4px)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem' }}>
          <div className="ai-card" style={{ width: '100%', maxWidth: '480px', padding: '1.75rem', position: 'relative' }}>
            <button
              onClick={() => setRoleModalOpen(false)}
              style={{ position: 'absolute', right: '1.25rem', top: '1.25rem', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
            >
              <X size={20} />
            </button>

            <h3 style={{ fontSize: '1.15rem', color: '#F8FAFC', margin: '0 0 0.5rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Shield size={20} color="var(--accent-cyan)" /> Change User Account Role
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: '0 0 1.25rem 0' }}>
              Target User: <strong style={{ color: '#F8FAFC' }}>{roleEditUser.full_name}</strong> ({roleEditUser.email})
            </p>

            {/* ERROR BANNER FOR LAST ADMIN PROTECTION */}
            {roleUpdateError && (
              <div style={{ padding: '0.85rem 1rem', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.4)', color: '#FCA5A5', fontSize: '0.85rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <AlertTriangle size={18} color="#EF4444" style={{ flexShrink: 0 }} />
                <span>{roleUpdateError}</span>
              </div>
            )}

            {roleUpdateSuccess && (
              <div style={{ padding: '0.85rem 1rem', borderRadius: '8px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.4)', color: '#6EE7B7', fontSize: '0.85rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Check size={18} color="var(--accent-emerald)" />
                <span>{roleUpdateSuccess}</span>
              </div>
            )}

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', fontSize: '0.875rem' }}>
              <div>
                <label style={{ display: 'block', color: 'var(--text-secondary)', marginBottom: '0.35rem', fontWeight: 600 }}>
                  Select New Canonical Role:
                </label>
                <select
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.65rem 0.85rem',
                    borderRadius: '8px',
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    border: '1px solid var(--border-color)',
                    color: '#F8FAFC',
                    fontSize: '0.875rem'
                  }}
                >
                  <option value="researcher">Researcher</option>
                  <option value="startup_founder">Startup Founder</option>
                  <option value="administrator">Administrator</option>
                </select>
              </div>

              <div style={{ padding: '0.85rem', borderRadius: '8px', background: 'rgba(30, 41, 59, 0.5)', border: '1px solid var(--border-color)', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                <strong>Confirmation:</strong> Change role from <span style={{ color: 'var(--accent-cyan-light)' }}>{roleEditUser.role}</span> to <span style={{ color: '#C084FC' }}>{newRole}</span>?
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button
                  type="button"
                  onClick={() => setRoleModalOpen(false)}
                  style={{ padding: '0.55rem 1rem', borderRadius: '8px', background: 'transparent', border: '1px solid var(--border-color)', color: 'var(--text-secondary)', cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  disabled={roleUpdateLoading}
                  onClick={handleSaveRoleChange}
                  className="btn-ai-primary"
                  style={{ padding: '0.55rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
                >
                  {roleUpdateLoading ? 'Updating...' : 'Confirm Role Change'}
                </button>
              </div>

            </div>
          </div>
        </div>
      )}

    </AppLayout>
  )
}

export default UserManagement
