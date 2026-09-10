<script setup>
import { ref } from 'vue'

import { searchTrips } from './api/trips'
import StayResultsTable from './components/StayResultsTable.vue'
import StaySearch from './components/StaySearch.vue'

const trips = ref([])
const error = ref('')
const isLoading = ref(false)
const searchedHotelName = ref('')

async function handleSearch(hotelName) {
  trips.value = []
  error.value = ''
  searchedHotelName.value = ''

  const normalizedHotelName = hotelName.trim()
  if (!normalizedHotelName) {
    error.value = 'Enter a hotel name to search.'
    return
  }

  isLoading.value = true

  try {
    trips.value = await searchTrips(normalizedHotelName)
    searchedHotelName.value = normalizedHotelName
  } catch (requestError) {
    error.value = requestError.message || 'Trips could not be loaded. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <main class="page-shell">
    <section class="travel-card" aria-labelledby="page-title">
      <header class="hero">
        <p class="eyebrow">Hudson Travel</p>
        <h1 id="page-title">Find an offered stay</h1>
        <p class="intro">Search by hotel name to see its available fixed-date stays.</p>
      </header>

      <StaySearch :is-loading="isLoading" @search="handleSearch" />

      <div class="status" aria-live="polite" aria-atomic="true">
        <p v-if="isLoading">Searching available stays…</p>
        <p v-else-if="error" class="error-message">{{ error }}</p>
        <p v-else-if="searchedHotelName && trips.length === 0" class="empty-message">
          No hotels or offered stays matched “{{ searchedHotelName }}”.
        </p>
        <p v-else-if="searchedHotelName" class="result-summary">
          {{ trips.length }} {{ trips.length === 1 ? 'stay' : 'stays' }} found for
          {{ searchedHotelName }}.
        </p>
      </div>

      <StayResultsTable v-if="trips.length" :trips="trips" />
    </section>
  </main>
</template>
