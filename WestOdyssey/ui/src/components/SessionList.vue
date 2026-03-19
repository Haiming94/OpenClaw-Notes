<template>
  <div class="session-panel">
    <div class="panel-header">
      <span class="panel-title">会话列表</span>
      <div class="header-actions">
        <button v-if="loading" class="loading-indicator" disabled>
          <span class="spin"></span>
        </button>
        <button class="refresh-btn" title="刷新" @click="$emit('refresh')">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6"/><path d="M1 20v-6h6"/>
            <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>
          </svg>
        </button>
        <button class="new-btn" @click="$emit('create')">+ 新建</button>
      </div>
    </div>

    <div class="session-list">
      <div
        v-for="sess in sessions"
        :key="sess.id"
        class="session-item"
        :class="{ active: sess.id === activeId }"
        @click="$emit('switch', sess.id)"
      >
        <div class="session-main">
          <span class="session-dot" :class="{ 'dot-active': sess.id === activeId }"></span>
          <div v-if="editingId === sess.id" class="title-edit" @click.stop>
            <input
              ref="editInputRef"
              v-model="editText"
              class="title-input"
              maxlength="20"
              @keydown.enter="finishEdit(sess)"
              @keydown.escape="cancelEdit"
              @blur="finishEdit(sess)"
            />
          </div>
          <div v-else class="session-info">
            <span class="session-title">{{ sess.title }}</span>
            <span v-if="sess.updatedAt" class="session-time">{{ formatTime(sess.updatedAt) }}</span>
          </div>
        </div>
        <div class="session-actions" @click.stop>
          <button class="action-icon" title="重命名" @click="startEdit(sess)">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
          </button>
          <button class="action-icon delete" title="删除" @click="$emit('delete', sess.id)">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 6h18"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
            </svg>
          </button>
        </div>
      </div>

      <div v-if="sessions.length === 0 && !loading" class="empty-hint">暂无会话</div>
      <div v-if="sessions.length === 0 && loading" class="empty-hint">加载中...</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import type { Session } from '../stores/chat'

defineProps<{
  sessions: Session[]
  activeId: string
  loading?: boolean
}>()

const emit = defineEmits<{
  create: []
  switch: [id: string]
  clear: []
  delete: [id: string]
  rename: [id: string, title: string]
  refresh: []
}>()

const editingId = ref<string | null>(null)
const editText = ref('')
const editInputRef = ref<HTMLInputElement[]>()

function startEdit(sess: Session) {
  editingId.value = sess.id
  editText.value = sess.customTitle || sess.title
  nextTick(() => {
    const inputs = editInputRef.value
    if (inputs && inputs.length > 0) inputs[0].focus()
  })
}

function finishEdit(sess: Session) {
  if (!editingId.value) return
  const trimmed = editText.value.trim()
  if (trimmed && trimmed !== sess.title) {
    emit('rename', sess.id, trimmed)
  }
  editingId.value = null
}

function cancelEdit() {
  editingId.value = null
}

function formatTime(ts: number): string {
  const d = new Date(ts)
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin}分钟前`
  const diffHour = Math.floor(diffMin / 60)
  if (diffHour < 24) return `${diffHour}小时前`
  const diffDay = Math.floor(diffHour / 24)
  if (diffDay < 7) return `${diffDay}天前`
  return `${d.getMonth() + 1}/${d.getDate()}`
}
</script>

<style scoped>
.session-panel {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  flex: 1;
  min-height: 0;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-title {
  font-size: 12px;
  font-weight: 600;
  color: rgba(100, 200, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.header-actions {
  display: flex;
  gap: 4px;
  align-items: center;
}

.refresh-btn {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: 1px solid rgba(100, 200, 255, 0.15);
  background: transparent;
  color: rgba(100, 200, 255, 0.5);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.refresh-btn:hover {
  background: rgba(100, 200, 255, 0.08);
  color: rgba(100, 200, 255, 0.8);
}

.loading-indicator {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spin {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(100, 200, 255, 0.15);
  border-top-color: rgba(100, 200, 255, 0.6);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.new-btn {
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid rgba(100, 200, 255, 0.2);
  background: rgba(100, 200, 255, 0.06);
  color: #b0e0ff;
  cursor: pointer;
  transition: all 0.2s;
}

.new-btn:hover {
  background: rgba(100, 200, 255, 0.12);
  border-color: rgba(100, 200, 255, 0.35);
}

.session-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 8px;
  border-radius: 8px;
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.session-item:hover {
  background: rgba(100, 200, 255, 0.05);
}

.session-item.active {
  background: rgba(100, 200, 255, 0.08);
  border-color: rgba(100, 200, 255, 0.15);
}

.session-main {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.session-dot {
  width: 6px;
  height: 6px;
  min-width: 6px;
  border-radius: 50%;
  background: rgba(100, 200, 255, 0.2);
}

.dot-active {
  background: #4caf50;
  box-shadow: 0 0 6px rgba(76, 175, 80, 0.4);
}

.session-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.session-title {
  font-size: 12px;
  color: #c0dff0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-time {
  font-size: 10px;
  color: rgba(100, 200, 255, 0.25);
}

.session-actions {
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.15s;
}

.session-item:hover .session-actions {
  opacity: 1;
}

.action-icon {
  width: 22px;
  height: 22px;
  border-radius: 4px;
  border: none;
  background: transparent;
  color: rgba(100, 200, 255, 0.4);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.action-icon:hover {
  background: rgba(100, 200, 255, 0.1);
  color: rgba(100, 200, 255, 0.8);
}

.action-icon.delete:hover {
  background: rgba(255, 100, 100, 0.1);
  color: rgba(255, 120, 120, 0.8);
}

.title-edit {
  flex: 1;
  min-width: 0;
}

.title-input {
  width: 100%;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid rgba(100, 200, 255, 0.3);
  background: rgba(0, 0, 0, 0.3);
  color: #e0f0ff;
  outline: none;
  font-family: inherit;
}

.title-input:focus {
  border-color: rgba(100, 200, 255, 0.5);
}

.empty-hint {
  padding: 20px;
  text-align: center;
  font-size: 12px;
  color: rgba(100, 200, 255, 0.25);
}

.session-list::-webkit-scrollbar { width: 3px; }
.session-list::-webkit-scrollbar-track { background: transparent; }
.session-list::-webkit-scrollbar-thumb {
  background: rgba(100, 200, 255, 0.12);
  border-radius: 2px;
}
</style>
