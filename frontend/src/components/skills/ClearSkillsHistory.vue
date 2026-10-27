<script setup>
import { onBeforeUnmount, ref } from 'vue'
import { createHistoryClear } from '../../skills/historyClear.js'
const emit = defineEmits(['intent', 'cleared', 'crisis', 'leave'])
const dialog = ref(null)
const state = ref({ busy: false, ready: false, attempted: false, error: '', success: false })
const controller = createHistoryClear({
  onIntent: () => emit('intent'), onCleared: result => emit('cleared', result),
  onChange(result) { state.value = result; if (result.success) dialog.value?.close() },
})
function open() { dialog.value.showModal(); controller.prepare() }
function close() { dialog.value.close() }
function crisis() { close(); emit('crisis') }
function leave() { close(); emit('leave') }
onBeforeUnmount(() => controller.dispose())
</script>

<template>
  <section class="history-clear" aria-label="Clear skills history">
    <button type="button" @click="open">Clear saved skills history</button>
    <p v-if="state.success" role="status">Saved skills history cleared. Display choices were kept.</p>
    <p v-else-if="state.attempted && state.error" role="alert">Could not confirm whether history was cleared. Reopen this control to retry the same request or review saved history.</p>
    <dialog ref="dialog" aria-labelledby="clear-skills-title">
      <h2 id="clear-skills-title">Clear saved skills history?</h2>
      <p>This permanently removes all saved skills sessions, checkpoints, conversations, messages, and conversation-run records in this local app. It also discards this view's unsaved exercise changes. Saved display choices, the live-call allowance ledger, and Hudson Travel records stay.</p>
      <p>Earlier saves and retries cannot restore cleared records. New sessions and conversations can still be saved.</p>
      <p v-if="state.busy" role="status">{{ state.attempted ? 'Clearing history… You can close this panel or leave.' : 'Checking history status…' }}</p>
      <p v-if="state.error" role="alert">{{ state.error }} {{ state.attempted ? 'The outcome may be unknown. Retry the same request; this will not clear newer history a second time.' : 'History has not been cleared by this control.' }}</p>
      <div class="clear-actions">
        <button autofocus type="button" @click="close">{{ state.attempted ? 'Close' : 'Cancel' }}</button>
        <button v-if="!state.attempted" type="button" :disabled="state.busy || !state.ready" @click="controller.confirm">Clear permanently</button>
        <button v-else-if="state.error" type="button" :disabled="state.busy" @click="controller.confirm">Retry same clear request</button>
        <button v-if="state.error && !state.attempted" type="button" :disabled="state.busy" @click="controller.prepare">Refresh confirmation</button>
        <button type="button" @click="crisis">Crisis support</button>
        <button type="button" @click="leave">Leave</button>
      </div>
    </dialog>
  </section>
</template>

<style scoped>
.history-clear { margin-top: 1.4rem; border-top: 1px solid #bac8bf; padding-top: 1rem; }
button { padding: 0.75rem; background: #355e51; }
dialog { width: min(36rem, calc(100% - 1.5rem)); max-height: 85dvh; overflow-y: auto; padding: 1.3rem; border: 1px solid #607a72; border-radius: 0.8rem; color: #253c35; background: #fafaf6; }
dialog::backdrop { background: rgb(25 40 35 / 45%); }
.clear-actions { display: flex; flex-wrap: wrap; gap: 0.6rem; }
button:focus-visible { outline: 3px solid #547e71; outline-offset: 3px; }
</style>
