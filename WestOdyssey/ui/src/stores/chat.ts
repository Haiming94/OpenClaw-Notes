import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { RESEARCH_AGENTS, COORDINATOR_AGENT, type AgentDef } from './agents'
import {
  listBackendSessions,
  loadChatHistory,
  type BackendSession,
} from '../composables/useSessionApi'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  agentId: string
  agentName?: string
  agentEmoji?: string
  timestamp: number
}

export interface Session {
  id: string
  agentId: string
  title: string
  customTitle?: string
  key?: string
  messages: ChatMessage[]
  createdAt: number
  updatedAt?: number
  loaded?: boolean
}

const TITLES_KEY = 'research-studio-titles'
const ACTIVE_KEY = 'research-studio-active-sessions'

function uid(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}

function sessionKey(agentId: string, sessionId: string): string {
  return `agent:${agentId}:main:webchat-user:default:${sessionId}`
}

function loadFromStorage<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key)
    if (raw) return JSON.parse(raw)
  } catch {}
  return fallback
}

function saveToStorage(key: string, value: unknown): void {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch {}
}

function generateShortTitle(text: string): string {
  const clean = text
    .replace(/\[.*?\]/g, '')
    .replace(/<[^>]+>/g, '')
    .replace(/\s+/g, ' ')
    .trim()
  if (!clean) return '新会话'
  if (clean.length <= 10) return clean
  const cut = clean.slice(0, 10)
  const lastPunct = Math.max(
    cut.lastIndexOf('，'),
    cut.lastIndexOf(','),
    cut.lastIndexOf('。'),
    cut.lastIndexOf('、'),
    cut.lastIndexOf(' '),
  )
  return (lastPunct > 4 ? cut.slice(0, lastPunct) : cut).trim() + '…'
}

export const useChatStore = defineStore('chat', () => {
  const activeAgentId = ref<string>(RESEARCH_AGENTS[0].id)
  const sessions = ref<Record<string, Session[]>>({})
  const activeSessionIds = ref<Record<string, string>>(loadFromStorage(ACTIVE_KEY, {}))
  const generatingAgents = ref<Record<string, boolean>>({})
  const streamingContent = ref('')
  const customTitles = ref<Record<string, string>>(loadFromStorage(TITLES_KEY, {}))
  const loadingAgents = ref<Record<string, boolean>>({})

  watch(activeSessionIds, (val) => saveToStorage(ACTIVE_KEY, val), { deep: true })
  watch(customTitles, (val) => saveToStorage(TITLES_KEY, val), { deep: true })

  function isAgentGenerating(agentId: string): boolean {
    return !!generatingAgents.value[agentId]
  }

  function setAgentGenerating(agentId: string, val: boolean) {
    generatingAgents.value[agentId] = val
  }

  function isAgentLoading(agentId: string): boolean {
    return !!loadingAgents.value[agentId]
  }

  async function loadBackendSessions(agentId: string): Promise<void> {
    if (loadingAgents.value[agentId]) return
    loadingAgents.value[agentId] = true
    try {
      const backendSessions = await listBackendSessions(agentId)
      const mapped: Session[] = backendSessions.map((bs) => {
        const savedTitle = customTitles.value[bs.key || '']
        let title = savedTitle || ''
        if (!title && bs.firstUserMsg) {
          title = generateShortTitle(bs.firstUserMsg)
        }
        if (!title) title = '新会话'
        return {
          id: bs.sessionId,
          agentId: bs.agentId || agentId,
          title,
          customTitle: savedTitle,
          key: bs.key,
          messages: [],
          createdAt: bs.updatedAt || Date.now(),
          updatedAt: bs.updatedAt || undefined,
          loaded: false,
        }
      })
      sessions.value[agentId] = mapped
      if (mapped.length > 0) {
        const activeId = activeSessionIds.value[agentId]
        if (!activeId || !mapped.find((s) => s.id === activeId)) {
          activeSessionIds.value[agentId] = mapped[0].id
        }
      }
    } catch (e) {
      console.error(`Failed to load sessions for ${agentId}:`, e)
    } finally {
      loadingAgents.value[agentId] = false
    }
  }

  async function loadSessionMessages(agentId: string, sessionId: string): Promise<void> {
    const agentSessions = sessions.value[agentId] || []
    const sess = agentSessions.find((s) => s.id === sessionId)
    if (!sess) return
    if (sess.loaded) return

    try {
      const history = await loadChatHistory(agentId, sessionId)
      const agentDef = getAgentById(agentId)
      const msgs: ChatMessage[] = []
      for (const m of history) {
        if (m.role !== 'user' && m.role !== 'assistant') continue
        const text = m.content
          .replace(/<final>([\s\S]*?)<\/final>/g, '$1')
          .replace(/<[^>]+>/g, '')
          .trim()
        if (!text) continue
        msgs.push({
          id: uid(),
          role: m.role,
          content: text,
          agentId,
          agentName: m.role === 'assistant' ? agentDef?.name : undefined,
          agentEmoji: m.role === 'assistant' ? agentDef?.emoji : undefined,
          timestamp: Date.now(),
        })
      }
      sess.messages = msgs
      sess.loaded = true

      if (!sess.customTitle && msgs.length > 0) {
        const firstUser = msgs.find((m) => m.role === 'user')
        if (firstUser && sess.title === '新会话') {
          sess.title = generateShortTitle(firstUser.content)
        }
      }
    } catch (e) {
      console.error(`Failed to load messages for ${agentId}:${sessionId}:`, e)
    }
  }

  function ensureSession(agentId: string): Session {
    if (!sessions.value[agentId] || sessions.value[agentId].length === 0) {
      const sess: Session = {
        id: uid(),
        agentId,
        title: '新会话',
        messages: [],
        createdAt: Date.now(),
        loaded: true,
      }
      if (!sessions.value[agentId]) sessions.value[agentId] = []
      sessions.value[agentId].push(sess)
      activeSessionIds.value[agentId] = sess.id
      return sess
    }
    const activeId = activeSessionIds.value[agentId]
    const found = sessions.value[agentId].find((s) => s.id === activeId)
    if (found) return found
    const first = sessions.value[agentId][0]
    activeSessionIds.value[agentId] = first.id
    return first
  }

  const currentSession = computed(() => ensureSession(activeAgentId.value))
  const currentMessages = computed(() => currentSession.value.messages)

  function getSessionKey(agentId?: string): string {
    const aid = agentId || activeAgentId.value
    const sess = ensureSession(aid)
    return sess.key || sessionKey(aid, sess.id)
  }

  function setActiveAgent(agentId: string) {
    activeAgentId.value = agentId
  }

  function createSession(agentId: string) {
    const sess: Session = {
      id: uid(),
      agentId,
      title: '新会话',
      messages: [],
      createdAt: Date.now(),
      loaded: true,
    }
    if (!sessions.value[agentId]) sessions.value[agentId] = []
    sessions.value[agentId].unshift(sess)
    activeSessionIds.value[agentId] = sess.id
  }

  function switchSession(agentId: string, sessionId: string) {
    activeSessionIds.value[agentId] = sessionId
  }

  function addMessage(agentId: string, msg: ChatMessage) {
    const sess = ensureSession(agentId)
    sess.messages.push(msg)
    sess.updatedAt = Date.now()
    if (msg.role === 'user' && sess.title === '新会话') {
      sess.title = generateShortTitle(msg.content)
    }
  }

  function clearSession(agentId: string) {
    const sess = ensureSession(agentId)
    sess.messages = []
    sess.title = '新会话'
    sess.loaded = true
    delete customTitles.value[sess.key || '']
  }

  function removeSession(agentId: string, sessionId: string) {
    const agentSessions = sessions.value[agentId] || []
    const idx = agentSessions.findIndex((s) => s.id === sessionId)
    if (idx < 0) return
    const sess = agentSessions[idx]
    if (sess.key) delete customTitles.value[sess.key]
    agentSessions.splice(idx, 1)
    if (activeSessionIds.value[agentId] === sessionId) {
      if (agentSessions.length > 0) {
        activeSessionIds.value[agentId] = agentSessions[0].id
      } else {
        delete activeSessionIds.value[agentId]
      }
    }
  }

  function renameSession(agentId: string, sessionId: string, newTitle: string) {
    const agentSessions = sessions.value[agentId] || []
    const sess = agentSessions.find((s) => s.id === sessionId)
    if (!sess) return
    const trimmed = newTitle.trim()
    if (!trimmed) return
    sess.title = trimmed
    sess.customTitle = trimmed
    if (sess.key) {
      customTitles.value[sess.key] = trimmed
    }
  }

  function getAgentSessions(agentId: string): Session[] {
    return sessions.value[agentId] || []
  }

  function getActiveAgent(): AgentDef {
    const all = [...RESEARCH_AGENTS, COORDINATOR_AGENT]
    return all.find((a) => a.id === activeAgentId.value) || RESEARCH_AGENTS[0]
  }

  function getAgentById(id: string): AgentDef | undefined {
    const all = [...RESEARCH_AGENTS, COORDINATOR_AGENT]
    return all.find((a) => a.id === id)
  }

  return {
    activeAgentId,
    sessions,
    activeSessionIds,
    generatingAgents,
    streamingContent,
    customTitles,
    loadingAgents,
    currentSession,
    currentMessages,
    isAgentGenerating,
    setAgentGenerating,
    isAgentLoading,
    loadBackendSessions,
    loadSessionMessages,
    getSessionKey,
    setActiveAgent,
    createSession,
    switchSession,
    addMessage,
    clearSession,
    removeSession,
    renameSession,
    getAgentSessions,
    getActiveAgent,
    ensureSession,
  }
})
