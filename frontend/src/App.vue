<script setup>
import { onBeforeUnmount, ref } from 'vue'
import TravelView from './components/TravelView.vue'
import SkillsExperience from './components/skills/SkillsExperience.vue'

const view = ref(window.location.hash === '#skills' ? 'skills' : 'travel')
function syncView() {
  view.value = window.location.hash === '#skills' ? 'skills' : 'travel'
}
window.addEventListener('hashchange', syncView)
onBeforeUnmount(() => window.removeEventListener('hashchange', syncView))
</script>

<template>
  <nav class="app-navigation" aria-label="Application views">
    <a href="#travel" :aria-current="view === 'travel' ? 'page' : undefined">Hudson Travel</a>
    <a href="#skills" :aria-current="view === 'skills' ? 'page' : undefined">Skills Prototype</a>
  </nav>
  <KeepAlive>
    <TravelView v-if="view === 'travel'" />
    <SkillsExperience v-else />
  </KeepAlive>
</template>

<style scoped>
.app-navigation { display: flex; gap: 1.5rem; padding: 0.85rem 1.25rem; background: #fff; }
.app-navigation a { color: #244842; text-underline-offset: 0.3em; }
.app-navigation [aria-current] { font-weight: 750; }
.app-navigation a:focus-visible { outline: 3px solid #527b72; outline-offset: 4px; }
</style>
