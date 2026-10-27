<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { loadSkillsConversation, loadSkillsConversations } from '../../api/skills.js'
const conversations = ref([])
const selected = ref(null)
const messages = ref([])
const nextCursor = ref(null)
const nextSequence = ref(null)
const error = ref('')
const busy = ref(false)
let generation = 0
async function refresh(more = false) {
  const token = ++generation
  selected.value = null; messages.value = []; error.value = ''; busy.value = true
  if (!more) conversations.value = []
  try {
    const result = await loadSkillsConversations(more ? nextCursor.value : null)
    if (token !== generation) return
    conversations.value = more ? [...conversations.value, ...result.conversations] : result.conversations
    nextCursor.value = result.next_cursor
  } catch (failure) { if (token === generation) error.value = failure.message }
  finally { if (token === generation) busy.value = false }
}
async function open(id, more = false) {
  const token = ++generation
  const after = more ? nextSequence.value : 0
  if (!more) { selected.value = null; messages.value = [] }
  error.value = ''; busy.value = true
  try {
    const result = await loadSkillsConversation(id, after)
    if (token !== generation) return
    selected.value = result.conversation
    messages.value = more ? [...messages.value, ...result.messages] : result.messages
    nextSequence.value = result.next_after_sequence
  } catch (failure) {
    if (token === generation) { selected.value = null; messages.value = []; error.value = failure.message }
  } finally { if (token === generation) busy.value = false }
}
onMounted(() => refresh())
onBeforeUnmount(() => { generation += 1 })
</script>

<template>
  <section aria-labelledby="conversation-history-title">
    <h2 id="conversation-history-title">Saved conversation history</h2>
    <p>Fictional local messages. Replies are not evidence of clinical improvement. Open a conversation to see its text.</p>
    <button type="button" :disabled="busy" @click="refresh()">Refresh conversation history</button>
    <p v-if="busy" role="status">Loading conversation history…</p>
    <p v-if="error" role="alert">{{ error }}</p>
    <p v-if="!busy && !error && !conversations.length">No conversations are saved.</p>
    <ul><li v-for="item in conversations" :key="item.conversation_id"><button type="button" @click="open(item.conversation_id)">Conversation · {{ item.placement }} breathing · {{ new Date(item.created_at).toLocaleString() }}</button></li></ul>
    <button v-if="nextCursor" type="button" :disabled="busy" @click="refresh(true)">More conversations</button>
    <article v-if="selected" aria-label="Saved conversation">
      <h3>Saved conversation · {{ selected.placement }} breathing</h3>
      <p>Read-only history. Return to exercise options to start a new optional conversation.</p>
      <ol><li v-for="message in messages" :key="message.message_id"><strong>{{ message.role === 'user' ? 'Fictional message' : message.source === 'application-fallback' ? 'Application fallback' : message.source === 'live-selected-template' ? 'Reviewed model selection' : 'Mock reply' }}</strong><p>{{ message.content }}</p></li></ol>
      <button v-if="nextSequence" type="button" :disabled="busy" @click="open(selected.conversation_id, true)">More messages</button>
    </article>
  </section>
</template>

<style scoped>
button { padding: 0.75rem; background: #355e51; margin: 0.4rem 0; text-align: left; }
li p { white-space: pre-wrap; overflow-wrap: anywhere; }
button:focus-visible { outline: 3px solid #547e71; outline-offset: 3px; }
</style>
