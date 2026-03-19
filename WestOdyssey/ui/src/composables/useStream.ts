const GATEWAY_URL = '/v1/chat/completions'
const AUTH_TOKEN = import.meta.env.VITE_OPENCLAW_AUTH_TOKEN || '142c139e22fba4a4ba87a736913a5168284b1fd0b72fe86d'

export interface StreamCallbacks {
  onChunk: (text: string) => void
  onDone: (fullText: string) => void
  onError: (error: string) => void
  onAbort?: (partialText: string) => void
}

export async function chatStream(
  agentId: string,
  sessionKey: string,
  messages: Array<{ role: string; content: string }>,
  callbacks: StreamCallbacks,
  signal?: AbortSignal,
): Promise<void> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-OpenClaw-Agent-Id': agentId,
    'X-OpenClaw-Session-Key': sessionKey,
  }
  if (AUTH_TOKEN) {
    headers['Authorization'] = `Bearer ${AUTH_TOKEN}`
  }

  const body = JSON.stringify({
    model: `openclaw:${agentId}`,
    messages,
    stream: true,
  })

  try {
    const resp = await fetch(GATEWAY_URL, { method: 'POST', headers, body, signal })

    if (!resp.ok) {
      callbacks.onError(`API 错误: ${resp.status} ${resp.statusText}`)
      return
    }

    const reader = resp.body?.getReader()
    if (!reader) {
      callbacks.onError('无法读取响应流')
      return
    }

    const decoder = new TextDecoder()
    let buffer = ''
    let fullText = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed || !trimmed.startsWith('data:')) continue

        const data = trimmed.slice(5).trim()
        if (data === '[DONE]') {
          callbacks.onDone(fullText)
          return
        }

        try {
          const parsed = JSON.parse(data)
          const content = parsed.choices?.[0]?.delta?.content
          if (content) {
            fullText += content
            callbacks.onChunk(content)
          }
          if (parsed.choices?.[0]?.finish_reason === 'stop') {
            callbacks.onDone(fullText)
            return
          }
        } catch {
          // skip unparseable
        }
      }
    }

    callbacks.onDone(fullText)
  } catch (e: any) {
    if (e.name === 'AbortError') {
      callbacks.onAbort?.(e.message || '')
      return
    }
    callbacks.onError(e.message || '连接错误')
  }
}
