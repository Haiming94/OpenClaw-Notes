<template>
  <div class="agent-chat">
    <div class="chat-header">
      <div class="header-info">
        <img v-if="agent.avatar" :src="agent.avatar" :alt="agent.name" class="header-avatar-img" />
        <span v-else class="header-emoji">{{ agent.emoji }}</span>
        <div>
          <h3 class="header-name" :style="{ color: agent.color }">{{ agent.name }}</h3>
          <p class="header-desc">{{ agent.description }}</p>
        </div>
      </div>
      <div class="header-badge" :style="{ borderColor: agent.color + '40', color: agent.color }">
        {{ agent.role }}
      </div>
    </div>

    <div class="chat-body">
      <div class="messages-area" ref="messagesRef">
        <div v-if="messages.length === 0 && !isStreaming && !loadingHistory" class="welcome-screen">
          <img v-if="agent.avatar" :src="agent.avatar" :alt="agent.name" class="welcome-avatar-img" />
          <div v-else class="welcome-emoji">{{ agent.emoji }}</div>
          <h3 class="welcome-title">你好，我是{{ agent.name }}</h3>
          <p class="welcome-desc">{{ agent.description }}</p>
          <div class="welcome-hints">
            <span class="hint-tag" v-for="(hint, i) in hints" :key="i">{{ hint }}</span>
          </div>
        </div>

        <div v-if="loadingHistory" class="loading-history">
          <span class="spin"></span>
          <span>加载历史记录...</span>
        </div>

        <ChatMessage
          v-for="msg in messages"
          :key="msg.id"
          :msg="msg"
          :is-streaming="msg.id === streamingMsgId"
        />

        <ChatMessage
          v-if="isStreaming && streamingMsg"
          :msg="streamingMsg"
          :is-streaming="true"
        />
      </div>

      <div class="sidebar-area">
        <SessionList
          :sessions="sessions"
          :active-id="activeSessionId"
          :loading="chatStore.isAgentLoading(props.agentId)"
          @create="handleCreateSession"
          @switch="handleSwitchSession"
          @clear="handleClearSession"
          @delete="handleDeleteSession"
          @rename="handleRenameSession"
          @refresh="handleRefresh"
        />

        <div class="agent-detail">
          <div class="detail-label">当前模型</div>
          <div class="detail-value">openclaw:{{ agent.id }}</div>
        </div>
      </div>
    </div>

    <ChatInput
      :placeholder="placeholderText"
      :generating="chatStore.isAgentGenerating(props.agentId)"
      @send="handleSend"
      @stop="handleStop"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, nextTick, watch, onMounted } from 'vue'
import ChatMessage from '../components/ChatMessage.vue'
import ChatInput from '../components/ChatInput.vue'
import SessionList from '../components/SessionList.vue'
import { useChatStore, type ChatMessage as ChatMsg } from '../stores/chat'
import { getAgentById, RESEARCH_AGENTS } from '../stores/agents'
import { chatStream } from '../composables/useStream'

const props = defineProps<{ agentId: string }>()
const chatStore = useChatStore()
const messagesRef = ref<HTMLElement>()

const agent = computed(() => getAgentById(props.agentId) || RESEARCH_AGENTS[0])
const placeholderText = computed(() => `向 ${agent.value.name} 提问...`)

const messages = computed(() => {
  const sess = chatStore.ensureSession(props.agentId)
  return sess.messages
})

const sessions = computed(() => chatStore.getAgentSessions(props.agentId))
const activeSessionId = computed(() => chatStore.activeSessionIds[props.agentId] || '')

const isStreaming = ref(false)
const streamingMsg = ref<ChatMsg | null>(null)
const streamingMsgId = ref('')
const loadingHistory = ref(false)
let currentAbort: AbortController | null = null

const hints = computed(() => {
  const map: Record<string, string[]> = {
    sanzang: ['制定研究计划', '分析研究方向', '协调任务优先级'],
    wukong: ['编写代码', '调试模型', '构建实验 pipeline'],
    wuneng: ['撰写论文', '润色表达', '基金申请书'],
    wujing: ['检索文献', '生成综述', '知识库构建'],
    horse: ['自动化流程', '资源管理', '数据清洗'],
  }
  return map[props.agentId] || ['开始对话']
})

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

watch(messages, scrollToBottom, { deep: true })

onMounted(async () => {
  await chatStore.loadBackendSessions(props.agentId)
  const sess = chatStore.ensureSession(props.agentId)
  if (!sess.loaded && sess.key) {
    loadingHistory.value = true
    await chatStore.loadSessionMessages(props.agentId, sess.id)
    loadingHistory.value = false
    scrollToBottom()
  }
})

function handleCreateSession() {
  chatStore.createSession(props.agentId)
}

async function handleSwitchSession(id: string) {
  chatStore.switchSession(props.agentId, id)
  const sess = chatStore.getAgentSessions(props.agentId).find((s) => s.id === id)
  if (sess && !sess.loaded && sess.key) {
    loadingHistory.value = true
    await chatStore.loadSessionMessages(props.agentId, id)
    loadingHistory.value = false
    scrollToBottom()
  }
}

function handleClearSession() {
  chatStore.clearSession(props.agentId)
}

function handleDeleteSession(id: string) {
  chatStore.removeSession(props.agentId, id)
}

function handleRenameSession(id: string, title: string) {
  chatStore.renameSession(props.agentId, id, title)
}

async function handleRefresh() {
  await chatStore.loadBackendSessions(props.agentId)
}

function finalizeStreaming() {
  if (streamingMsg.value && streamingMsg.value.content) {
    const finalMsg: ChatMsg = { ...streamingMsg.value }
    chatStore.addMessage(props.agentId, finalMsg)
  }
  streamingMsg.value = null
  isStreaming.value = false
  chatStore.setAgentGenerating(props.agentId, false)
  currentAbort = null
}

function handleStop() {
  if (currentAbort) {
    currentAbort.abort()
  }
  finalizeStreaming()
}

async function handleSend(text: string) {
  if (currentAbort) {
    currentAbort.abort()
    finalizeStreaming()
  }

  const uid = Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
  const userMsg: ChatMsg = {
    id: uid,
    role: 'user',
    content: text,
    agentId: props.agentId,
    timestamp: Date.now(),
  }
  chatStore.addMessage(props.agentId, userMsg)
  scrollToBottom()

  chatStore.setAgentGenerating(props.agentId, true)
  isStreaming.value = true
  const assistantId = 'stream-' + Date.now().toString(36)
  streamingMsg.value = {
    id: assistantId,
    role: 'assistant',
    content: '',
    agentId: props.agentId,
    agentName: agent.value.name,
    agentEmoji: agent.value.emoji,
    timestamp: Date.now(),
  }

  const abort = new AbortController()
  currentAbort = abort

  const sessionKey = chatStore.getSessionKey(props.agentId)
  const history = messages.value
    .filter((m) => m.role === 'user' || m.role === 'assistant')
    .slice(-40)
    .map((m) => ({ role: m.role, content: m.content }))

  await chatStream(props.agentId, sessionKey, history, {
    onChunk: (chunk) => {
      if (streamingMsg.value && currentAbort === abort) {
        streamingMsg.value.content += chunk
        scrollToBottom()
      }
    },
    onDone: (fullText) => {
      if (currentAbort !== abort) return
      const finalMsg: ChatMsg = {
        id: assistantId,
        role: 'assistant',
        content: fullText,
        agentId: props.agentId,
        agentName: agent.value.name,
        agentEmoji: agent.value.emoji,
        timestamp: Date.now(),
      }
      chatStore.addMessage(props.agentId, finalMsg)
      streamingMsg.value = null
      isStreaming.value = false
      chatStore.setAgentGenerating(props.agentId, false)
      currentAbort = null
    },
    onError: (error) => {
      if (currentAbort !== abort) return
      const errMsg: ChatMsg = {
        id: assistantId,
        role: 'assistant',
        content: `Error: ${error}`,
        agentId: props.agentId,
        agentName: agent.value.name,
        agentEmoji: agent.value.emoji,
        timestamp: Date.now(),
      }
      chatStore.addMessage(props.agentId, errMsg)
      streamingMsg.value = null
      isStreaming.value = false
      chatStore.setAgentGenerating(props.agentId, false)
      currentAbort = null
    },
    onAbort: () => {},
  }, abort.signal)
}
</script>

<style scoped>
.agent-chat {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(180deg, #0b1e30 0%, #081620 100%);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 24px;
  border-bottom: 1px solid rgba(100, 200, 255, 0.08);
  background: rgba(255, 255, 255, 0.02);
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-avatar-img {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  object-fit: cover;
}

.header-emoji { font-size: 28px; }

.header-name {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
}

.header-desc {
  margin: 2px 0 0;
  font-size: 12px;
  color: rgba(100, 200, 255, 0.45);
}

.header-badge {
  font-size: 11px;
  padding: 4px 12px;
  border: 1px solid;
  border-radius: 20px;
  font-weight: 500;
}

.chat-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}

.sidebar-area {
  width: 220px;
  min-width: 220px;
  border-left: 1px solid rgba(100, 200, 255, 0.08);
  display: flex;
  flex-direction: column;
  background: rgba(0, 0, 0, 0.15);
}

.agent-detail {
  padding: 12px;
  border-top: 1px solid rgba(100, 200, 255, 0.06);
}

.detail-label {
  font-size: 10px;
  color: rgba(100, 200, 255, 0.35);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  font-size: 12px;
  color: rgba(100, 200, 255, 0.6);
  font-family: 'JetBrains Mono', monospace;
  margin-top: 4px;
}

.loading-history {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px;
  color: rgba(100, 200, 255, 0.4);
  font-size: 13px;
}

.spin {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(100, 200, 255, 0.15);
  border-top-color: rgba(100, 200, 255, 0.6);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.welcome-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 40px;
}

.welcome-avatar-img {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  object-fit: cover;
  margin-bottom: 16px;
  filter: drop-shadow(0 0 24px rgba(100, 200, 255, 0.2));
  animation: float 3s ease-in-out infinite;
}

.welcome-emoji {
  font-size: 56px;
  margin-bottom: 16px;
  filter: drop-shadow(0 0 24px rgba(100, 200, 255, 0.2));
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.welcome-title {
  font-size: 22px;
  font-weight: 700;
  color: #b0e0ff;
  margin: 0 0 8px;
}

.welcome-desc {
  font-size: 14px;
  color: rgba(100, 200, 255, 0.45);
  max-width: 400px;
  margin: 0 0 20px;
}

.welcome-hints {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}

.hint-tag {
  font-size: 12px;
  padding: 6px 14px;
  border-radius: 20px;
  background: rgba(100, 200, 255, 0.06);
  border: 1px solid rgba(100, 200, 255, 0.12);
  color: rgba(100, 200, 255, 0.6);
  cursor: default;
  transition: all 0.2s;
}

.hint-tag:hover {
  background: rgba(100, 200, 255, 0.1);
  border-color: rgba(100, 200, 255, 0.25);
}

.messages-area::-webkit-scrollbar { width: 4px; }
.messages-area::-webkit-scrollbar-track { background: transparent; }
.messages-area::-webkit-scrollbar-thumb {
  background: rgba(100, 200, 255, 0.15);
  border-radius: 2px;
}
</style>
