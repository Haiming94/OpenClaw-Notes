<template>
  <div class="app-layout">
    <NavBar :active-id="chatStore.activeAgentId" @select="handleSelectAgent" />
    <main class="main-content">
      <AgentChat
        v-if="chatStore.activeAgentId !== 'coordinator'"
        :agent-id="chatStore.activeAgentId"
        :key="chatStore.activeAgentId"
      />
      <GroupChat v-else />
    </main>
  </div>
</template>

<script setup lang="ts">
import NavBar from './components/NavBar.vue'
import AgentChat from './views/AgentChat.vue'
import GroupChat from './views/GroupChat.vue'
import { useChatStore } from './stores/chat'

const chatStore = useChatStore()

function handleSelectAgent(id: string) {
  chatStore.setActiveAgent(id)
}
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.main-content {
  flex: 1;
  overflow: hidden;
}
</style>
