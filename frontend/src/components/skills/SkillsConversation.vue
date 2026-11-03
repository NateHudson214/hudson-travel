<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { loadSkillsModelStatus } from '../../api/skills.js'
import { createConversation } from '../../skills/conversation.js'
const props = defineProps({ placement: { type: String, required: true }, sessionId: { type: String, default: null }, historyEpoch: { type: Number, required: true } })
const emit = defineEmits(['back'])
const draft = ref('')
const state = ref({ messages: [], busy: false, error: '', canRetry: false })
let conversation = null
let disposed = false
const mode = ref(null)
const modeError = ref('')
onMounted(async () => {
  try {
    const status = await loadSkillsModelStatus()
    if (disposed) return
    mode.value = status.mode
    conversation = createConversation({ placement: props.placement, sessionId: props.sessionId,
      historyEpoch: props.historyEpoch, allowLive: status.mode === 'live',
      onChange(result) { state.value = result } })
  } catch {
    if (!disposed) modeError.value = 'Conversation settings are unavailable. Continue without conversation.'
  }
})
async function submit() {
  await conversation?.submit(draft.value)
  if (!state.value.error && !state.value.canRetry) draft.value = ''
}
async function retry() {
  await conversation?.retry()
  if (!state.value.error && !state.value.canRetry) draft.value = ''
}
onBeforeUnmount(() => { disposed = true; conversation?.dispose() })
</script>

<template>
  <section aria-labelledby="skills-conversation-title" class="conversation">
    <h2 id="skills-conversation-title">Optional conversation · {{ placement }} breathing</h2>
    <p v-if="mode === 'mock'">Mock responses only. No live model is called. Fictional messages and replies are saved locally on this computer without encryption. Do not enter personal disclosures.</p>
    <p v-if="mode === 'mock'">This fixed mock demonstrates approved replies; it does not interpret your message or assess how you feel.</p>
    <p v-if="mode === 'live'">Live OpenAI conversation · gpt-6-luna. Sending shares your fictional message, recent conversation, session facts and saved display choices with OpenAI. Visible replies use reviewed application text. Messages and replies are saved locally without encryption. Do not enter personal disclosures. The host allowance is at most 10 calls and $1; it returns to mocks at the limit.</p>
    <p v-if="modeError" role="alert">{{ modeError }}</p>
    <p v-if="!mode && !modeError" role="status">Checking conversation settings… You can continue or leave.</p>
    <button type="button" @click="emit('back')">{{ placement === 'before' ? 'Continue to breathing without waiting' : 'Back to exercise options' }}</button>
    <ol aria-label="Conversation messages" aria-live="polite">
      <li v-for="message in state.messages" :key="message.message_id">
        <strong>{{ message.role === 'user' ? 'Fictional message' : message.source === 'application-fallback' ? 'Application fallback' : message.source === 'live-selected-template' ? 'Reviewed model selection' : 'Mock reply' }}</strong>
        <p>{{ message.content }}</p>
      </li>
    </ol>
    <form @submit.prevent="submit">
      <label for="skills-fictional-message">Fictional message (optional, up to 500 characters)</label>
      <textarea id="skills-fictional-message" v-model="draft" maxlength="500" rows="3" :disabled="!mode || state.busy || state.canRetry" />
      <button type="submit" :disabled="!mode || !draft.trim() || state.busy || state.canRetry">Send fictional message</button>
    </form>
    <p v-if="state.modeNotice" role="status">{{ state.modeNotice }}</p>
    <p v-if="state.busy" role="status">Saving conversation… You can continue or leave.</p>
    <p v-if="state.error" role="alert">{{ state.error }} Your draft remains here. Continue without it or retry the same turn.</p>
    <button v-if="state.canRetry" type="button" @click="retry">Retry same turn</button>
    <p v-if="mode === 'mock'">Leaving closes this conversation view. Already saved replies remain in history.</p>
    <p v-if="mode === 'live'">Leaving requests cancellation. An already dispatched call can still count toward the allowance; late replies cannot change the exercise. You can review saved messages in conversation history.</p>
  </section>
</template>

<style scoped>
.conversation { margin-top: 1.3rem; padding: 1rem; border: 1px solid #bac8bf; border-radius: 0.8rem; background: #fafbf7; }
button { padding: 0.75rem; background: #355e51; margin: 0.5rem 0; }
form { display: grid; gap: 0.6rem; } textarea { width: 100%; padding: 0.6rem; font: inherit; box-sizing: border-box; }
ol { padding-left: 1.2rem; } li p { white-space: pre-wrap; overflow-wrap: anywhere; }
button:focus-visible, textarea:focus-visible { outline: 3px solid #547e71; outline-offset: 3px; }
</style>
