import { defineConfig, type Plugin } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'fs'
import path from 'path'

const OPENCLAW_DIR = '/root/.openclaw'
const AGENTS_DIR = path.join(OPENCLAW_DIR, 'agents')

function parseJsonl(filePath: string): any[] {
  try {
    const content = fs.readFileSync(filePath, 'utf-8')
    return content.split('\n').filter(Boolean).map((line) => {
      try { return JSON.parse(line) } catch { return null }
    }).filter(Boolean)
  } catch {
    return []
  }
}

function getSessionMessages(agentId: string, sessionId: string) {
  const sessDir = path.join(AGENTS_DIR, agentId, 'sessions')
  const filePath = path.join(sessDir, `${sessionId}.jsonl`)
  if (!fs.existsSync(filePath)) return []
  const entries = parseJsonl(filePath)
  return entries
    .filter((e: any) => e.type === 'message')
    .map((e: any) => {
      const msg = e.message || {}
      let text = ''
      if (typeof msg.content === 'string') {
        text = msg.content
      } else if (Array.isArray(msg.content)) {
        text = msg.content
          .filter((b: any) => b.type === 'text' && b.text)
          .map((b: any) => b.text)
          .join('\n')
      }
      return { role: msg.role, content: text, timestamp: e.timestamp }
    })
    .filter((m: any) => m.role === 'user' || m.role === 'assistant')
}

function listSessions(agentId: string) {
  const sessDir = path.join(AGENTS_DIR, agentId, 'sessions')
  const indexPath = path.join(sessDir, 'sessions.json')
  if (!fs.existsSync(indexPath)) return []

  try {
    const index = JSON.parse(fs.readFileSync(indexPath, 'utf-8'))
    const results: any[] = []
    for (const [key, entry] of Object.entries(index) as any[]) {
      if (!key.includes(':webchat-user:') && !key.includes(':openai:')) continue
      const sessionId = entry.sessionId
      if (!sessionId) continue
      const jsonlPath = path.join(sessDir, `${sessionId}.jsonl`)
      if (!fs.existsSync(jsonlPath)) continue

      let firstUserMsg = ''
      let lastMsg = ''
      try {
        const content = fs.readFileSync(jsonlPath, 'utf-8')
        const lines = content.split('\n').filter(Boolean)
        for (const line of lines) {
          try {
            const obj = JSON.parse(line)
            if (obj.type !== 'message') continue
            const msg = obj.message || {}
            let text = ''
            if (typeof msg.content === 'string') {
              text = msg.content
            } else if (Array.isArray(msg.content)) {
              text = msg.content
                .filter((b: any) => b.type === 'text' && b.text)
                .map((b: any) => b.text)
                .join(' ')
            }
            if (msg.role === 'user' && !firstUserMsg) firstUserMsg = text.slice(0, 100)
            if (msg.role === 'user' || msg.role === 'assistant') lastMsg = text.slice(0, 100)
          } catch {}
        }
      } catch {}

      results.push({
        key,
        sessionId,
        agentId,
        updatedAt: entry.updatedAt || null,
        firstUserMsg,
        lastMsg,
      })
    }
    results.sort((a, b) => (b.updatedAt || 0) - (a.updatedAt || 0))
    return results
  } catch {
    return []
  }
}

function openclawApiPlugin(): Plugin {
  return {
    name: 'openclaw-session-api',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        if (!req.url?.startsWith('/api/openclaw/')) return next()

        const url = new URL(req.url, 'http://localhost')
        res.setHeader('Content-Type', 'application/json')

        if (url.pathname === '/api/openclaw/sessions') {
          const agentId = url.searchParams.get('agentId')
          if (!agentId) {
            res.statusCode = 400
            res.end(JSON.stringify({ error: 'agentId required' }))
            return
          }
          res.end(JSON.stringify({ sessions: listSessions(agentId) }))
          return
        }

        if (url.pathname === '/api/openclaw/history') {
          const agentId = url.searchParams.get('agentId')
          const sessionId = url.searchParams.get('sessionId')
          if (!agentId || !sessionId) {
            res.statusCode = 400
            res.end(JSON.stringify({ error: 'agentId and sessionId required' }))
            return
          }
          const messages = getSessionMessages(agentId, sessionId)
          res.end(JSON.stringify({ messages }))
          return
        }

        res.statusCode = 404
        res.end(JSON.stringify({ error: 'not found' }))
      })
    },
  }
}

export default defineConfig({
  plugins: [vue(), openclawApiPlugin()],
  server: {
    port: 8001,
    host: '0.0.0.0',
    proxy: {
      '/v1': {
        target: 'http://localhost:18789',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
  },
})
