<script setup>
import { ref } from 'vue'

defineProps({
  isLoading: {
    type: Boolean,
    required: true,
  },
})

const emit = defineEmits(['search'])
const hotelName = ref('')

function submitSearch() {
  emit('search', hotelName.value)
}
</script>

<template>
  <form class="search-form" @submit.prevent="submitSearch">
    <div class="input-group">
      <label for="hotel-name">Hotel name</label>
      <input
        id="hotel-name"
        v-model="hotelName"
        name="hotel-name"
        type="text"
        autocomplete="off"
        placeholder="Try Harbor Lantern Hotel"
        :disabled="isLoading"
      />
    </div>
    <button type="submit" :disabled="isLoading" :aria-busy="isLoading">
      {{ isLoading ? 'Searching…' : 'Search' }}
    </button>
  </form>
</template>
