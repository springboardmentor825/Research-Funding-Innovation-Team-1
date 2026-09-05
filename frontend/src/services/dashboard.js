const BASE = '/api'

export async function fetchDashboardStats() {
  const res = await fetch(`${BASE}/dashboard/stats`)
  if (!res.ok) throw new Error(`Stats request failed (${res.status})`)
  return res.json()
}

export async function fetchAllGrants() {
  const res = await fetch(`${BASE}/grants/`)
  if (!res.ok) throw new Error(`Grants request failed (${res.status})`)
  return res.json()
}
