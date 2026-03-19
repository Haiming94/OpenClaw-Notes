<template>
  <nav class="navbar">
    <div class="nav-brand">
      <div class="brand-icon">🔬</div>
      <div class="brand-text">
        <span class="brand-title">学术取经</span>
        <span class="brand-sub">智能科研协作系统</span>
      </div>
    </div>

    <div class="nav-agents">
      <button
        v-for="agent in agents"
        :key="agent.id"
        class="nav-agent-btn"
        :class="{ active: activeId === agent.id }"
        :style="activeId === agent.id ? { '--agent-color': agent.color } : {}"
        @click="$emit('select', agent.id)"
      >
        <img v-if="agent.avatar" :src="agent.avatar" :alt="agent.name" class="agent-avatar-img" />
        <span v-else class="agent-emoji">{{ agent.emoji }}</span>
        <span class="agent-name">{{ agent.name }}</span>
        <span class="agent-role">{{ agent.role }}</span>
        <div v-if="activeId === agent.id" class="active-indicator"></div>
      </button>
    </div>

    <div class="nav-divider"></div>

    <button
      class="nav-agent-btn coordinator-btn"
      :class="{ active: activeId === coordinator.id }"
      :style="activeId === coordinator.id ? { '--agent-color': coordinator.color } : {}"
      @click="$emit('select', coordinator.id)"
    >
      <span class="agent-emoji">{{ coordinator.emoji }}</span>
      <span class="agent-name">{{ coordinator.name }}</span>
      <span class="agent-role">{{ coordinator.role }}</span>
      <div v-if="activeId === coordinator.id" class="active-indicator"></div>
    </button>

    <div class="nav-footer">
      <div class="status-dot"></div>
      <span>Gateway 已连接</span>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { RESEARCH_AGENTS, COORDINATOR_AGENT } from '../stores/agents'

defineProps<{ activeId: string }>()
defineEmits<{ select: [id: string] }>()

const agents = RESEARCH_AGENTS
const coordinator = COORDINATOR_AGENT
</script>

<style scoped>
.navbar {
  width: 220px;
  min-width: 220px;
  height: 100vh;
  background: linear-gradient(180deg, #0a1929 0%, #0d2137 50%, #0a1929 100%);
  border-right: 1px solid rgba(100, 200, 255, 0.1);
  display: flex;
  flex-direction: column;
  padding: 16px 12px;
  gap: 6px;
  overflow-y: auto;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 8px 16px;
  margin-bottom: 4px;
}

.brand-icon {
  font-size: 28px;
  filter: drop-shadow(0 0 8px rgba(100, 200, 255, 0.4));
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-size: 16px;
  font-weight: 700;
  color: #b0e0ff;
  letter-spacing: 2px;
}

.brand-sub {
  font-size: 10px;
  color: rgba(100, 200, 255, 0.45);
  margin-top: 2px;
}

.nav-agents {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-agent-btn {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 10px 12px;
  border: 1px solid transparent;
  border-radius: 10px;
  background: transparent;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  width: 100%;
  text-align: left;
}

.nav-agent-btn:hover {
  background: rgba(100, 200, 255, 0.06);
  border-color: rgba(100, 200, 255, 0.1);
}

.nav-agent-btn.active {
  background: linear-gradient(135deg, rgba(100, 200, 255, 0.1) 0%, rgba(77, 208, 225, 0.08) 100%);
  border-color: var(--agent-color, #64B5F6);
  box-shadow: 0 0 16px rgba(100, 200, 255, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.agent-avatar-img {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  object-fit: cover;
  margin-bottom: 2px;
}

.agent-emoji {
  font-size: 20px;
  margin-bottom: 2px;
}

.agent-name {
  font-size: 13px;
  font-weight: 600;
  color: #c0dff0;
  transition: color 0.2s;
}

.nav-agent-btn.active .agent-name {
  color: #e0f0ff;
}

.agent-role {
  font-size: 10px;
  color: rgba(176, 224, 255, 0.35);
  margin-top: 1px;
}

.nav-agent-btn.active .agent-role {
  color: rgba(176, 224, 255, 0.6);
}

.active-indicator {
  position: absolute;
  right: -12px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 24px;
  border-radius: 3px 0 0 3px;
  background: var(--agent-color, #64B5F6);
  box-shadow: 0 0 12px var(--agent-color, #64B5F6);
}

.nav-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(100, 200, 255, 0.15), transparent);
  margin: 8px 0;
}

.coordinator-btn {
  background: rgba(38, 198, 218, 0.04);
}

.coordinator-btn:hover {
  background: rgba(38, 198, 218, 0.08);
}

.nav-footer {
  margin-top: auto;
  padding: 12px 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: rgba(100, 200, 255, 0.35);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #4caf50;
  box-shadow: 0 0 8px rgba(76, 175, 80, 0.6);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>
