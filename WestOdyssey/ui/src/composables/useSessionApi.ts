export interface BackendSession {
  key: string
  sessionId: string
  agentId: string
  updatedAt: number | null
  firstUserMsg: string
  lastMsg: string
}

export interface HistoryMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

export async function listBackendSessions(agentId: string): Promise<BackendSession[]> {
  const resp = await fetch(`/api/openclaw/sessions?agentId=${encodeURIComponent(agentId)}`)
  if (!resp.ok) return []
  const data = await resp.json()
  return data.sessions || []
}

export async function loadChatHistory(
  agentId: string,
  sessionId: string,
): Promise<HistoryMessage[]> {
  const resp = await fetch(
    `/api/openclaw/history?agentId=${encodeURIComponent(agentId)}&sessionId=${encodeURIComponent(sessionId)}`,
  )
  if (!resp.ok) return []
  const data = await resp.json()
  return data.messages || []
}
