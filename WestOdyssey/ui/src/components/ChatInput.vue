<template>
  <div class="chat-input-wrapper">
    <div class="input-container" :class="{ focused: isFocused }">
      <textarea
        ref="textareaRef"
        v-model="text"
        :placeholder="placeholder"
        class="chat-textarea"
        rows="1"
        @focus="isFocused = true"
        @blur="isFocused = false"
        @input="autoResize"
        @keydown.enter.exact="handleAction"
      ></textarea>
      <button
        v-if="generating"
        class="stop-btn"
        @click="handleStop"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
          <rect x="6" y="6" width="12" height="12" rx="2" />
        </svg>
      </button>
      <button
        v-else
        class="send-btn"
        :disabled="!text.trim()"
        @click="handleAction"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 2L11 13" /><path d="M22 2L15 22L11 13L2 9L22 2Z" />
        </svg>
      </button>
    </div>
    <div v-if="generating" class="generating-hint">
      <span class="loading-dots">思考中</span>
      <span class="hint-tip">（可继续输入或点击停止）</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'

defineProps<{
  placeholder?: string
  generating?: boolean
}>()

const emit = defineEmits<{ send: [text: string]; stop: [] }>()

const text = ref('')
const isFocused = ref(false)
const textareaRef = ref<HTMLTextAreaElement>()

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}

function handleAction(e?: Event) {
  e?.preventDefault()
  const msg = text.value.trim()
  if (!msg) return
  emit('send', msg)
  text.value = ''
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  })
}

function handleStop() {
  emit('stop')
}
</script>

<style scoped>
.chat-input-wrapper {
  padding: 16px 20px 12px;
  background: linear-gradient(180deg, transparent, rgba(10, 25, 41, 0.8));
}

.input-container {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(100, 200, 255, 0.12);
  border-radius: 14px;
  padding: 8px 8px 8px 16px;
  transition: all 0.25s;
}

.input-container.focused {
  border-color: rgba(100, 200, 255, 0.35);
  box-shadow: 0 0 20px rgba(100, 200, 255, 0.06);
  background: rgba(255, 255, 255, 0.05);
}

.chat-textarea {
  flex: 1;
  border: none;
  background: transparent;
  color: #e0f0ff;
  font-size: 14px;
  line-height: 1.5;
  resize: none;
  outline: none;
  max-height: 160px;
  font-family: inherit;
}

.chat-textarea::placeholder {
  color: rgba(100, 200, 255, 0.3);
}

.send-btn {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #64B5F6, #4DD0E1);
  color: #0a1929;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 0 16px rgba(100, 200, 255, 0.3);
}

.send-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.stop-btn {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 10px;
  border: 1px solid rgba(255, 120, 120, 0.4);
  background: rgba(255, 80, 80, 0.15);
  color: #ff8888;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.stop-btn:hover {
  background: rgba(255, 80, 80, 0.25);
  border-color: rgba(255, 120, 120, 0.6);
  transform: scale(1.05);
}

.generating-hint {
  text-align: center;
  padding: 6px 0 0;
  font-size: 12px;
  color: rgba(100, 200, 255, 0.5);
}

.hint-tip {
  margin-left: 6px;
  color: rgba(100, 200, 255, 0.3);
  font-size: 11px;
}

.loading-dots::after {
  content: '';
  animation: dots 1.5s steps(3, end) infinite;
}

@keyframes dots {
  0% { content: ''; }
  33% { content: '.'; }
  66% { content: '..'; }
  100% { content: '...'; }
}
</style>
