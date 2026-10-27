<script setup>
import { ref } from 'vue'
import { CRISIS_RESOURCES as resources } from '../../skills/crisisResources.js'

const emit = defineEmits(['closed', 'leave'])
const dialog = ref(null)
function open() { if (!dialog.value.open) dialog.value.showModal() }
function close() { dialog.value.close() }
function leave() { close(); emit('leave') }
defineExpose({ open, close })
</script>

<template>
  <dialog ref="dialog" class="crisis-dialog" aria-labelledby="crisis-title" @close="emit('closed')">
    <header>
      <h2 id="crisis-title">Crisis support — {{ resources.region }}</h2>
      <div class="dialog-actions">
        <button autofocus type="button" @click="close">Back</button>
        <button type="button" @click="leave">Leave experience</button>
      </div>
    </header>
    <p>{{ resources.name }} offers phone, text, and online chat support in the United States and its territories.</p>
    <ul>
      <li><a :href="resources.call">Call 988</a></li>
      <li><a :href="resources.text">Text 988</a></li>
      <li><a :href="resources.chat" target="_blank" rel="noopener noreferrer">Open Lifeline web chat</a></li>
    </ul>
    <p>This information opens locally, even if session storage is unavailable. External services need phone or internet access.</p>
    <p>This coursework prototype is for fictional testing only. It is not therapy or monitored support.</p>
    <p class="source">Contacts checked {{ resources.reviewed }}. <a :href="resources.source" target="_blank" rel="noopener noreferrer">Official resource information</a></p>
  </dialog>
</template>

<style scoped>
.crisis-dialog { width: min(36rem, calc(100% - 1.5rem)); max-height: 85dvh; padding: 1.4rem; border: 1px solid #607a72; border-radius: 0.8rem; color: #253c35; background: #fafaf6; }
.crisis-dialog::backdrop { background: rgb(25 40 35 / 45%); }
header { position: sticky; top: -1.4rem; padding: 0.5rem 0; background: #fafaf6; }
h2 { font-size: 1.35rem; }
.dialog-actions { display: flex; flex-wrap: wrap; gap: 0.6rem; margin-top: 0.8rem; }
button { padding: 0.6rem 0.85rem; background: #355e51; }
a { color: #254f44; text-underline-offset: 0.2em; }
li { margin: 0.9rem 0; }
.source { font-size: 0.85rem; }
button:focus-visible, a:focus-visible { outline: 3px solid #547e71; outline-offset: 4px; }
</style>
