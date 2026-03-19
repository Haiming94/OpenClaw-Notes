<template>
  <div class="group-chat">
    <div class="chat-header">
      <div class="header-info">
        <span class="header-emoji">&#x1F3DB;&#xFE0F;</span>
        <div>
          <h3 class="header-name">学术讨论空间</h3>
          <p class="header-desc">科研团队协作中心，任务分发与协调汇总</p>
        </div>
      </div>
      <div class="team-avatars">
        <span
          v-for="a in teamAgents"
          :key="a.id"
          class="team-avatar"
          :title="a.name"
          :style="{ borderColor: a.color + '60' }"
        >
          <img v-if="a.avatar" :src="a.avatar" :alt="a.name" class="team-avatar-img" />
          <span v-else>{{ a.emoji }}</span>
        </span>
      </div>
    </div>

    <div class="chat-body">
      <div class="messages-area" ref="messagesRef">
        <div v-if="messages.length === 0 && !isStreaming && !loadingHistory" class="welcome-screen">
          <div class="welcome-emoji">&#x1F3DB;&#xFE0F;</div>
          <h3 class="welcome-title">欢迎来到学术讨论空间</h3>
          <p class="welcome-desc">
            在这里您可以同时和唐僧、孙悟空、猪八戒、沙僧、白龙马 5 个科研成员协作。
            系统会自动分析您的需求，将任务分配给合适的团队成员。
          </p>
          <div class="team-grid">
            <div v-for="a in teamAgents" :key="a.id" class="team-card" :style="{ borderColor: a.color + '30' }">
              <img v-if="a.avatar" :src="a.avatar" :alt="a.name" class="team-card-img" />
              <span v-else class="team-card-emoji">{{ a.emoji }}</span>
              <span class="team-card-name" :style="{ color: a.color }">{{ a.name }}</span>
              <span class="team-card-role">{{ a.role }}</span>
            </div>
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
        <div class="team-panel">
          <div class="panel-title">团队成员</div>
          <div v-for="a in teamAgents" :key="a.id" class="team-member">
            <img v-if="a.avatar" :src="a.avatar" :alt="a.name" class="member-img" />
            <span v-else class="member-emoji">{{ a.emoji }}</span>
            <span class="member-name">{{ a.name }}</span>
          </div>
        </div>

        <SessionList
          :sessions="sessions"
          :active-id="activeSessionId"
          :loading="chatStore.isAgentLoading(AGENT_ID)"
          @create="handleCreate"
          @switch="handleSwitchSession"
          @clear="handleClear"
          @delete="handleDeleteSession"
          @rename="handleRenameSession"
          @refresh="handleRefresh"
        />

        <div class="action-btns">
          <button class="action-btn clear" @click="handleClear">&#x1F5D1;&#xFE0F; 清空当前</button>
        </div>
      </div>
    </div>

    <ChatInput
      placeholder="向学术讨论空间发布任务..."
      :generating="chatStore.isAgentGenerating(AGENT_ID)"
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
import { RESEARCH_AGENTS, COORDINATOR_AGENT } from '../stores/agents'
import { chatStream } from '../composables/useStream'

const AGENT_ID = 'coordinator'
const chatStore = useChatStore()
const messagesRef = ref<HTMLElement>()
const teamAgents = RESEARCH_AGENTS

const messages = computed(() => {
  const sess = chatStore.ensureSession(AGENT_ID)
  return sess.messages
})

const sessions = computed(() => chatStore.getAgentSessions(AGENT_ID))
const activeSessionId = computed(() => chatStore.activeSessionIds[AGENT_ID] || '')

const isStreaming = ref(false)
const streamingMsg = ref<ChatMsg | null>(null)
const streamingMsgId = ref('')
const loadingHistory = ref(false)
let currentAbort: AbortController | null = null

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

watch(messages, scrollToBottom, { deep: true })

onMounted(async () => {
  await chatStore.loadBackendSessions(AGENT_ID)
  const sess = chatStore.ensureSession(AGENT_ID)
  if (!sess.loaded && sess.key) {
    loadingHistory.value = true
    await chatStore.loadSessionMessages(AGENT_ID, sess.id)
    loadingHistory.value = false
    scrollToBottom()
  }
})

function handleCreate() {
  chatStore.createSession(AGENT_ID)
}

async function handleSwitchSession(id: string) {
  chatStore.switchSession(AGENT_ID, id)
  const sess = chatStore.getAgentSessions(AGENT_ID).find((s) => s.id === id)
  if (sess && !sess.loaded && sess.key) {
    loadingHistory.value = true
    await chatStore.loadSessionMessages(AGENT_ID, id)
    loadingHistory.value = false
    scrollToBottom()
  }
}

function handleClear() {
  chatStore.clearSession(AGENT_ID)
}

function handleDeleteSession(id: string) {
  chatStore.removeSession(AGENT_ID, id)
}

function handleRenameSession(id: string, title: string) {
  chatStore.renameSession(AGENT_ID, id, title)
}

async function handleRefresh() {
  await chatStore.loadBackendSessions(AGENT_ID)
}

function finalizeStreaming() {
  if (streamingMsg.value && streamingMsg.value.content) {
    const finalMsg: ChatMsg = { ...streamingMsg.value }
    chatStore.addMessage(AGENT_ID, finalMsg)
  }
  streamingMsg.value = null
  isStreaming.value = false
  chatStore.setAgentGenerating(AGENT_ID, false)
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
    agentId: AGENT_ID,
    timestamp: Date.now(),
  }
  chatStore.addMessage(AGENT_ID, userMsg)
  scrollToBottom()

  chatStore.setAgentGenerating(AGENT_ID, true)
  isStreaming.value = true
  const assistantId = 'stream-' + Date.now().toString(36)
  streamingMsg.value = {
    id: assistantId,
    role: 'assistant',
    content: '',
    agentId: AGENT_ID,
    agentName: COORDINATOR_AGENT.name,
    agentEmoji: COORDINATOR_AGENT.emoji,
    timestamp: Date.now(),
  }

  const abort = new AbortController()
  currentAbort = abort

  const sessionKey = chatStore.getSessionKey(AGENT_ID)
  const history = messages.value
    .filter((m) => m.role === 'user' || m.role === 'assistant')
    .slice(-40)
    .map((m) => ({ role: m.role, content: m.content }))

  await chatStream(AGENT_ID, sessionKey, history, {
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
        agentId: AGENT_ID,
        agentName: COORDINATOR_AGENT.name,
        agentEmoji: COORDINATOR_AGENT.emoji,
        timestamp: Date.now(),
      }
      chatStore.addMessage(AGENT_ID, finalMsg)
      streamingMsg.value = null
      isStreaming.value = false
      chatStore.setAgentGenerating(AGENT_ID, false)
      currentAbort = null
    },
    onError: (error) => {
      if (currentAbort !== abort) return
      const errMsg: ChatMsg = {
        id: assistantId,
        role: 'assistant',
        content: `Error: ${error}`,
        agentId: AGENT_ID,
        agentName: COORDINATOR_AGENT.name,
        agentEmoji: COORDINATOR_AGENT.emoji,
        timestamp: Date.now(),
      }
      chatStore.addMessage(AGENT_ID, errMsg)
      streamingMsg.value = null
      isStreaming.value = false
      chatStore.setAgentGenerating(AGENT_ID, false)
      currentAbort = null
    },
    onAbort: () => {},
  }, abort.signal)
}
</script>

<style scoped>
.group-chat {
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
  border-bottom: 1px solid rgba(38, 198, 218, 0.1);
  background: rgba(38, 198, 218, 0.02);
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-emoji { font-size: 28px; }

.header-name {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: #26C6DA;
}

.header-desc {
  margin: 2px 0 0;
  font-size: 12px;
  color: rgba(38, 198, 218, 0.45);
}

.team-avatars {
  display: flex;
  gap: 4px;
}

.team-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  background: rgba(255, 255, 255, 0.03);
  overflow: hidden;
}

.team-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
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
  border-left: 1px solid rgba(38, 198, 218, 0.08);
  display: flex;
  flex-direction: column;
  background: rgba(0, 0, 0, 0.15);
  padding: 12px;
  gap: 12px;
}

.panel-title {
  font-size: 12px;
  font-weight: 600;
  color: rgba(38, 198, 218, 0.6);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.team-member {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  font-size: 13px;
  color: #c0dff0;
}

.member-img {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  object-fit: cover;
}

.member-emoji { font-size: 16px; }

.action-btns {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.action-btn {
  font-size: 11px;
  padding: 8px;
  border-radius: 8px;
  border: 1px solid rgba(38, 198, 218, 0.2);
  background: rgba(38, 198, 218, 0.04);
  color: rgba(38, 198, 218, 0.7);
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: rgba(38, 198, 218, 0.1);
}

.action-btn.clear {
  border-color: rgba(255, 100, 100, 0.15);
  background: rgba(255, 100, 100, 0.04);
  color: rgba(255, 150, 150, 0.6);
}

.loading-history {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px;
  color: rgba(38, 198, 218, 0.4);
  font-size: 13px;
}

.spin {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(38, 198, 218, 0.15);
  border-top-color: rgba(38, 198, 218, 0.6);
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

.welcome-emoji {
  font-size: 56px;
  margin-bottom: 16px;
  filter: drop-shadow(0 0 24px rgba(38, 198, 218, 0.2));
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.welcome-title {
  font-size: 22px;
  font-weight: 700;
  color: #26C6DA;
  margin: 0 0 8px;
}

.welcome-desc {
  font-size: 14px;
  color: rgba(100, 200, 255, 0.45);
  max-width: 500px;
  margin: 0 0 24px;
  line-height: 1.6;
}

.team-grid {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}

.team-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid;
  background: rgba(255, 255, 255, 0.02);
  min-width: 80px;
  transition: all 0.2s;
}

.team-card:hover {
  background: rgba(255, 255, 255, 0.04);
  transform: translateY(-2px);
}

.team-card-img {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  object-fit: cover;
  margin-bottom: 4px;
}

.team-card-emoji {
  font-size: 24px;
  margin-bottom: 4px;
}

.team-card-name {
  font-size: 13px;
  font-weight: 600;
}

.team-card-role {
  font-size: 10px;
  color: rgba(100, 200, 255, 0.35);
  margin-top: 2px;
}

.messages-area::-webkit-scrollbar { width: 4px; }
.messages-area::-webkit-scrollbar-track { background: transparent; }
.messages-area::-webkit-scrollbar-thumb {
  background: rgba(38, 198, 218, 0.15);
  border-radius: 2px;
}
</style>
