<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { appendSkillsEvent, loadSkillsSession, loadSkillsSessions } from '../../api/skills.js'

const props = defineProps({ initialId: { type: String, default: '' } })
const emit = defineEmits(['reconciled'])
const sessions = ref([])
const nextCursor = ref(null)
const selected = ref(null)
const events = ref([])
const historyEpoch = ref(0)
const nextSequence = ref(null)
const error = ref('')
const loading = ref(false)
let generation = 0
let disposed = false

async function refresh(more = false) {
  const token = ++generation
  error.value = ''; selected.value = null; events.value = []; loading.value = true
  if (!more) sessions.value = []
  try {
    const result = await loadSkillsSessions(more ? nextCursor.value : null)
    if (token !== generation) return
    sessions.value = more ? [...sessions.value, ...result.sessions] : result.sessions
    nextCursor.value = result.next_cursor
  } catch (failure) { if (token === generation) error.value = failure.message }
  finally { if (token === generation) loading.value = false }
}

async function open(sessionId, more = false) {
  const token = ++generation
  const after = more ? nextSequence.value : 0
  if (!more) { selected.value = null; events.value = [] }
  error.value = ''; loading.value = true
  try {
    const result = await loadSkillsSession(sessionId, after)
    if (token !== generation) return
    historyEpoch.value = result.history_epoch
    selected.value = result.session
    if (props.initialId === sessionId && ['completed', 'stopped', 'interrupted'].includes(result.session.status)) emit('reconciled', sessionId)
    events.value = more ? [...events.value, ...result.events] : result.events
    nextSequence.value = result.next_after_sequence
  } catch (failure) {
    if (token === generation) { selected.value = null; events.value = []; error.value = failure.message }
  } finally { if (token === generation) loading.value = false }
}

async function markInterrupted() {
  const saved = selected.value
  if (!saved) return
  const token = ++generation
  error.value = ''; loading.value = true
  const snapshot = Object.fromEntries([
    'active_ms', 'pause_ms', 'support_ms', 'setup_ms', 'cycles_completed', 'phase', 'phase_remaining_ms',
  ].map((key) => [key, saved[key]]))
  try {
    const result = await appendSkillsEvent(saved.session_id, {
      history_epoch: historyEpoch.value, event_id: crypto.randomUUID(), sequence: saved.revision + 1,
      expected_revision: saved.revision, kind: 'interrupt', snapshot, reason: null,
    })
    if (token === generation) {
      sessions.value = sessions.value.map((session) => session.session_id === saved.session_id ? result.session : session)
      emit('reconciled', saved.session_id)
      await open(saved.session_id)
    }
  } catch (failure) { if (token === generation) error.value = failure.message }
  finally { if (token === generation) loading.value = false }
}

onMounted(async () => { await refresh(); if (!disposed && props.initialId) await open(props.initialId) })
onBeforeUnmount(() => { disposed = true; generation += 1 })
</script>

<template>
  <section aria-labelledby="skills-history-title">
    <h2 id="skills-history-title">Saved session history</h2>
    <p>History shows saved checkpoints, not clinical improvement. An interrupted duration may be incomplete.</p>
    <button type="button" :disabled="loading" @click="refresh(false)">Refresh session history</button>
    <p v-if="loading" role="status">Loading saved history…</p>
    <p v-if="error" role="alert">{{ error }}</p>
    <p v-if="!loading && !error && !sessions.length">No sessions are saved.</p>
    <ul class="session-list">
      <li v-for="session in sessions" :key="session.session_id">
        <button type="button" @click="open(session.session_id)">
          Paced breathing · {{ session.status }} · {{ new Date(session.created_at).toLocaleString() }}
        </button>
      </li>
    </ul>
    <button v-if="nextCursor" type="button" :disabled="loading" @click="refresh(true)">More sessions</button>
    <article v-if="selected" class="session-detail" aria-label="Session details">
      <h3>Paced breathing — {{ selected.status }}</h3>
      <p class="session-id">Session {{ selected.session_id }}</p>
      <dl>
        <dt>Reported active time</dt><dd>{{ (selected.active_ms / 1000).toFixed(2) }} seconds</dd>
        <dt>Setup</dt><dd>{{ (selected.setup_ms / 1000).toFixed(2) }} seconds</dd>
        <dt>Other pauses</dt><dd>{{ (selected.pause_ms / 1000).toFixed(2) }} seconds</dd>
        <dt>Crisis panel time</dt><dd>{{ (selected.support_ms / 1000).toFixed(2) }} seconds</dd>
        <dt>Cycles completed</dt><dd>{{ selected.cycles_completed }} of 6</dd>
      </dl>
      <p>Timing is client-reported; the database does not independently verify rendered cues.</p>
      <p v-if="['ready', 'running', 'paused'].includes(selected.status)">This saved session will not restart automatically. If it is no longer active in another tab, you can mark it interrupted.</p>
      <button v-if="['ready', 'running', 'paused'].includes(selected.status)" type="button" :disabled="loading" @click="markInterrupted">Mark saved session interrupted</button>
      <details>
        <summary>Saved checkpoints</summary>
        <ol><li v-for="event in events" :key="event.event_id">{{ event.sequence }}. {{ event.kind }} · {{ event.snapshot.phase }} · {{ event.snapshot.active_ms }} active ms</li></ol>
        <button v-if="nextSequence" type="button" :disabled="loading" @click="open(selected.session_id, true)">More checkpoints</button>
      </details>
    </article>
  </section>
</template>

<style scoped>
button { padding: 0.65rem 0.85rem; background: #355e51; text-align: left; }
li { margin: 0.65rem 0; }
.session-list { padding-left: 0; list-style: none; }
.session-detail { margin-top: 1.5rem; border-top: 1px solid #bac8bf; padding-top: 1rem; }
.session-id { overflow-wrap: anywhere; font-size: 0.85rem; }
dl { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; }
dd { margin: 0; } details { margin-top: 1rem; }
summary { cursor: pointer; }
</style>
