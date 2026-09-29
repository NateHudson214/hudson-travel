<script setup>
import { computed, ref } from 'vue'

import { searchNearbyHotels } from '../api/nearbyHotels.js'
import NearbyHotelsMap from './NearbyHotelsMap.vue'

const zipCode = ref('')
const location = ref(null)
const hotels = ref([])
const radiusMeters = ref(0)
const resultLimit = ref(0)
const selectedPlaceId = ref('')
const error = ref('')
const isLoading = ref(false)
const searchCompleted = ref(false)

const radiusKilometers = computed(() => radiusMeters.value / 1000)

function clearResults() {
  location.value = null
  hotels.value = []
  radiusMeters.value = 0
  resultLimit.value = 0
  selectedPlaceId.value = ''
  searchCompleted.value = false
}

function distanceLabel(distanceMeters) {
  if (distanceMeters === null || distanceMeters === undefined) {
    return ''
  }
  return `${Math.round(distanceMeters).toLocaleString()} m away`
}

async function submitSearch() {
  clearResults()
  error.value = ''

  const normalizedZipCode = zipCode.value.trim()
  if (!/^[0-9]{5}$/.test(normalizedZipCode)) {
    error.value = 'Enter a five-digit U.S. ZIP code.'
    return
  }

  isLoading.value = true

  try {
    const result = await searchNearbyHotels(normalizedZipCode)
    location.value = result.location
    hotels.value = result.hotels
    radiusMeters.value = result.radius_meters
    resultLimit.value = result.result_limit
    selectedPlaceId.value = result.hotels[0]?.place_id || ''
    searchCompleted.value = true
  } catch (requestError) {
    clearResults()
    error.value = requestError.message || 'Nearby hotels could not be loaded. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <section class="nearby-search" aria-labelledby="nearby-search-title">
    <div class="nearby-search-heading">
      <p class="eyebrow section-eyebrow">Assignment 2 Part 1</p>
      <h2 id="nearby-search-title">Find hotels near a U.S. ZIP code</h2>
      <p class="section-intro">
        Search live provider location data within five kilometres of the resolved ZIP point.
      </p>
    </div>

    <form class="nearby-search-form" novalidate @submit.prevent="submitSearch">
      <div class="input-group">
        <label for="nearby-zip-code">ZIP code</label>
        <input
          id="nearby-zip-code"
          v-model="zipCode"
          name="nearby-zip-code"
          type="text"
          inputmode="numeric"
          autocomplete="postal-code"
          placeholder="Enter five digits"
          :disabled="isLoading"
        />
      </div>
      <button type="submit" :disabled="isLoading" :aria-busy="isLoading">
        {{ isLoading ? 'Searching nearby hotels…' : 'Search nearby hotels' }}
      </button>
    </form>

    <div class="nearby-feedback" aria-live="polite" aria-atomic="true">
      <p v-if="isLoading">Resolving the ZIP and finding nearby hotels…</p>
      <p v-else-if="error" class="error-message">{{ error }}</p>
      <p v-else-if="searchCompleted && hotels.length === 0" class="empty-message">
        The ZIP resolved successfully, but no nearby hotels were returned within
        {{ radiusKilometers }} km.
      </p>
      <p v-else-if="!searchCompleted" class="empty-message">
        Enter a ZIP code to find nearby hotels.
      </p>
    </div>

    <div v-if="location" class="nearby-location" aria-label="Resolved search center">
      <div>
        <strong>Resolved search center:</strong>
        {{ location.postcode }}<template v-if="location.locality"> · {{ location.locality }}</template>
      </div>
      <dl class="nearby-location-details">
        <div>
          <dt>Country code</dt>
          <dd>{{ location.country_code }}</dd>
        </div>
        <div>
          <dt>Latitude</dt>
          <dd>{{ location.latitude }}</dd>
        </div>
        <div>
          <dt>Longitude</dt>
          <dd>{{ location.longitude }}</dd>
        </div>
      </dl>
    </div>

    <template v-if="location && hotels.length">
      <p class="nearby-result-summary">
        {{ hotels.length }} {{ hotels.length === 1 ? 'hotel' : 'hotels' }} returned by Geoapify.
        Results include up to {{ resultLimit }} hotels within {{ radiusKilometers }} km of the resolved point.
      </p>

      <div class="nearby-results-layout">
        <div class="nearby-hotel-list" aria-label="Nearby hotel results">
          <button
            v-for="(hotel, index) in hotels"
            :key="hotel.place_id"
            type="button"
            class="nearby-hotel-card"
            :class="{ 'nearby-hotel-selected': hotel.place_id === selectedPlaceId }"
            :aria-current="hotel.place_id === selectedPlaceId ? 'true' : undefined"
            @click="selectedPlaceId = hotel.place_id"
          >
            <span class="hotel-result-number">{{ index + 1 }}</span>
            <span class="hotel-result-copy">
              <strong>{{ hotel.name || 'Name unavailable' }}</strong>
              <span>{{ hotel.formatted_address || 'Address unavailable' }}</span>
              <span v-if="distanceLabel(hotel.distance_meters)" class="hotel-distance">
                {{ distanceLabel(hotel.distance_meters) }}
              </span>
            </span>
          </button>
          <p class="geoapify-attribution">Hotel data: Powered by Geoapify</p>
        </div>

        <NearbyHotelsMap
          :location="location"
          :hotels="hotels"
          :selected-place-id="selectedPlaceId"
          @select="selectedPlaceId = $event"
        />
      </div>
    </template>
  </section>
</template>
