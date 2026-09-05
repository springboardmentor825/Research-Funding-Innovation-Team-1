const BASE = '/api'

export async function fetchResearcherOverview() {
  const res = await fetch(`${BASE}/insights/researcher`)
  if (!res.ok) throw new Error(`Researcher overview failed (${res.status})`)
  return res.json()
}

export async function fetchPatentInsights() {
  const res = await fetch(`${BASE}/insights/patents`)
  if (!res.ok) throw new Error(`Patent insights failed (${res.status})`)
  return res.json()
}

export async function fetchPublicationInsights() {
  const res = await fetch(`${BASE}/insights/publications`)
  if (!res.ok) throw new Error(`Publication insights failed (${res.status})`)
  return res.json()
}

export async function fetchAlerts() {
  const res = await fetch(`${BASE}/insights/alerts`)
  if (!res.ok) throw new Error(`Alerts failed (${res.status})`)
  return res.json()
}
