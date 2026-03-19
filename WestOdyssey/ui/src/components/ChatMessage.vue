<template>
  <div class="chat-message" :class="[msg.role, { streaming: isStreaming }]">
    <div v-if="msg.role === 'user'" class="message-row user-row">
      <div class="message-bubble user-bubble">
        <div class="message-content" v-html="renderContent(msg.content)"></div>
      </div>
      <div class="avatar user-avatar">&#x1F464;</div>
    </div>

    <div v-else class="message-row assistant-row">
      <div class="avatar agent-avatar" :style="{ background: agentGradient }">
        <img v-if="agentDef?.avatar" :src="agentDef.avatar" :alt="msg.agentName" class="avatar-img" />
        <span v-else>{{ msg.agentEmoji || '&#x1F916;' }}</span>
      </div>
      <div class="message-bubble agent-bubble">
        <div class="agent-label" :style="{ color: agentColor }">
          {{ msg.agentName || 'Agent' }}
        </div>
        <div class="message-content" v-html="renderContent(msg.content)"></div>
        <span v-if="isStreaming" class="cursor-blink">&#x258C;</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import type { ChatMessage } from '../stores/chat'
import { getAgentById } from '../stores/agents'

const props = defineProps<{
  msg: ChatMessage
  isStreaming?: boolean
}>()

const agentDef = computed(() => getAgentById(props.msg.agentId))
const agentColor = computed(() => agentDef.value?.color || '#64B5F6')
const agentGradient = computed(() => {
  const c = agentColor.value
  return `linear-gradient(135deg, ${c}22, ${c}11)`
})

function renderContent(text: string): string {
  if (!text) return ''
  try {
    return marked.parse(text, { async: false }) as string
  } catch {
    return text
  }
}
</script>

<style scoped>
.chat-message {
  margin-bottom: 16px;
  animation: fadeSlideIn 0.3s ease-out;
}

@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  max-width: 85%;
}

.user-row {
  margin-left: auto;
  flex-direction: row;
  justify-content: flex-end;
}

.assistant-row {
  margin-right: auto;
}

.avatar {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 10px;
}

.user-avatar {
  background: linear-gradient(135deg, rgba(100, 181, 246, 0.15), rgba(77, 208, 225, 0.1));
  border: 1px solid rgba(100, 181, 246, 0.2);
}

.agent-avatar {
  border: 1px solid rgba(100, 200, 255, 0.15);
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 14px;
  line-height: 1.6;
  font-size: 14px;
}

.user-bubble {
  background: linear-gradient(135deg, rgba(100, 181, 246, 0.18) 0%, rgba(77, 208, 225, 0.12) 100%);
  border: 1px solid rgba(100, 181, 246, 0.2);
  color: #e0f0ff;
  border-bottom-right-radius: 4px;
}

.agent-bubble {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(100, 200, 255, 0.08);
  color: #c8dce8;
  border-bottom-left-radius: 4px;
}

.agent-label {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 6px;
  opacity: 0.9;
}

.message-content :deep(p) {
  margin: 0 0 8px;
}

.message-content :deep(p:last-child) {
  margin-bottom: 0;
}

.message-content :deep(pre) {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(100, 200, 255, 0.1);
  border-radius: 8px;
  padding: 12px;
  overflow-x: auto;
  font-size: 13px;
  margin: 8px 0;
}

.message-content :deep(code) {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px;
}

.message-content :deep(:not(pre) > code) {
  background: rgba(100, 200, 255, 0.1);
  color: #b0e0ff;
  padding: 2px 6px;
  border-radius: 4px;
}

.message-content :deep(ul), .message-content :deep(ol) {
  padding-left: 20px;
  margin: 4px 0;
}

.message-content :deep(blockquote) {
  border-left: 3px solid rgba(100, 200, 255, 0.3);
  padding-left: 12px;
  margin: 8px 0;
  color: rgba(200, 220, 232, 0.7);
}

.cursor-blink {
  animation: blink 0.8s step-end infinite;
  color: #64B5F6;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.streaming .agent-bubble {
  border-color: rgba(100, 200, 255, 0.2);
  box-shadow: 0 0 20px rgba(100, 200, 255, 0.05);
}
</style>
