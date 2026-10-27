<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { createDisplayPreferences, motionLabel } from '../../skills/preferences.js'
const props = defineProps({ simpler: Boolean, motion: { type: String, required: true } })
const emit = defineEmits(['apply'])
const state = ref({ busy: false, lastSetup: null, error: '', notice: '', canSave: false, canRetry: false })
const preferences = createDisplayPreferences({ apply: settings => emit('apply', settings), onChange: value => { state.value = value } })
onMounted(() => preferences.refresh())
onBeforeUnmount(() => preferences.dispose())
</script>

<template>
  <section class="display-choices" aria-labelledby="display-choices-title">
    <h3 id="display-choices-title">Display choices</h3>
    <p>Current: simpler view {{ props.simpler ? 'on' : 'off' }}; {{ motionLabel(props.motion) }}.</p>
    <p v-if="!props.simpler">Saving is optional. Saved choices are offered next time, never applied automatically.</p>
    <p v-if="state.lastSetup">Saved: simpler view {{ state.lastSetup.simpler_view ? 'on' : 'off' }}; {{ motionLabel(state.lastSetup.motion_mode) }}.</p>
    <p v-else-if="!state.busy && !state.error">No display setup is saved.</p>
    <div class="choice-actions">
      <button type="button" :disabled="state.busy || !state.canSave" @click="preferences.save({ simpler_view: props.simpler, motion_mode: props.motion })">Save display choices</button>
      <button v-if="state.lastSetup" type="button" :disabled="state.busy" @click="preferences.useLast">Use last setup</button>
      <button type="button" @click="preferences.reset">Reset display choices</button>
    </div>
    <p v-if="state.busy" role="status">Updating saved choices… You can start breathing or leave.</p>
    <p v-if="state.notice" role="status">{{ state.notice }}</p>
    <p v-if="state.error" role="alert">{{ state.error }} Current display controls still work. A local reset may not have cleared the saved copy; refresh before choosing again.</p>
    <button v-if="state.canRetry && !state.busy" type="button" @click="preferences.retry">Retry same display request</button>
    <button v-if="!props.simpler || state.error" type="button" :disabled="state.busy" @click="preferences.refresh">Refresh saved choices</button>
    <p v-if="!props.simpler" class="details">Reset restores the full view and device motion setting, and clears the saved setup. History stays saved. Device reduced motion always keeps the cue still. Requested saves or resets may finish after leaving.</p>
  </section>
</template>

<style scoped>
.display-choices { margin: 1.3rem 0 0; padding: 1rem; border-top: 1px solid #bac8bf; text-align: left; }
h3 { margin-top: 0; } p { margin: 0.6rem 0; }
.choice-actions { display: flex; gap: 0.5rem; flex-wrap: wrap; }
button { padding: 0.65rem 0.85rem; background: #355e51; margin: 0.25rem 0; }
.details { font-size: 0.85rem; }
button:focus-visible { outline: 3px solid #547e71; outline-offset: 3px; }
</style>
