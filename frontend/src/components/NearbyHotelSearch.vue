<script setup>
import { computed, onMounted, ref } from 'vue'

import { searchNearbyHotels } from '../api/nearbyHotels.js'
import {
  loadSavedHotelIds,
  removeSavedHotel,
  saveHotelLocally,
  searchSavedHotels,
} from '../api/savedHotels.js'
import NearbyHotelsMap from './NearbyHotelsMap.vue'

const zipCode = ref('')
const searchedZipCode = ref('')
const location = ref(null)
const hotels = ref([])
const radiusMeters = ref(0)
const resultLimit = ref(0)
const resultSource = ref('')
const selectedPlaceId = ref('')
const savedPlaceIds = ref(new Set())
const error = ref('')
const storageError = ref('')
const storageMessage = ref('')
const activeHotelId = ref('')
const activeHotelAction = ref('')
const isLoading = ref(false)
const searchCompleted = ref(false)

const radiusKilometers = computed(() => radiusMeters.value / 1000)
const isBusy = computed(() => isLoading.value || Boolean(activeHotelId.value))
const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
})

function clearResults() {
  searchedZipCode.value = ''
  location.value = null
  hotels.value = []
  radiusMeters.value = 0
  resultLimit.value = 0
  resultSource.value = ''
  selectedPlaceId.value = ''
  searchCompleted.value = false
}

function distanceLabel(distanceMeters) {
  if (distanceMeters === null || distanceMeters === undefined) {
    return ''
  }
  return `${Math.round(distanceMeters).toLocaleString()} m away`
}

function nightlyRateLabel(cents) {
  return currencyFormatter.format(cents / 100)
}

function isSaved(placeId) {
  return savedPlaceIds.value.has(placeId)
}

function setResult(result, source, normalizedZipCode) {
  searchedZipCode.value = normalizedZipCode
  location.value = result.location
  hotels.value = result.hotels
  resultSource.value = source
  radiusMeters.value = source === 'api' ? result.radius_meters : 0
  resultLimit.value = source === 'api' ? result.result_limit : result.hotels.length
  selectedPlaceId.value = result.hotels[0]?.place_id || ''
  searchCompleted.value = true
  if (source === 'local') {
    savedPlaceIds.value = new Set([
      ...savedPlaceIds.value,
      ...result.hotels.map((hotel) => hotel.place_id),
    ])
  }
}

async function refreshSavedStatus() {
  try {
    const result = await loadSavedHotelIds()
    savedPlaceIds.value = new Set(result.place_ids)
  } catch (requestError) {
    storageError.value = requestError.message || 'Saved hotel status could not be loaded. Please try again.'
  }
}

async function submitSearch() {
  clearResults()
  error.value = ''
  storageError.value = ''
  storageMessage.value = ''

  const normalizedZipCode = zipCode.value.trim()
  if (!/^[0-9]{5}$/.test(normalizedZipCode)) {
    error.value = 'Enter a five-digit U.S. ZIP code.'
    return
  }

  isLoading.value = true

  try {
    const localResult = await searchSavedHotels(normalizedZipCode)
    if (localResult.hotels.length) {
      setResult(localResult, 'local', normalizedZipCode)
      return
    }

    const apiResult = await searchNearbyHotels(normalizedZipCode)
    setResult(apiResult, 'api', normalizedZipCode)
  } catch (requestError) {
    clearResults()
    error.value = requestError.message || 'Nearby hotels could not be loaded. Please try again.'
  } finally {
    isLoading.value = false
  }
}

async function addHotel(hotel) {
  if (!location.value || !searchedZipCode.value || isSaved(hotel.place_id)) {
    return
  }
  storageError.value = ''
  storageMessage.value = ''
  activeHotelId.value = hotel.place_id
  activeHotelAction.value = 'save'

  try {
    const saved = await saveHotelLocally(hotel, searchedZipCode.value, location.value)
    savedPlaceIds.value = new Set([...savedPlaceIds.value, saved.hotel.place_id])
    storageMessage.value = `${saved.hotel.name || 'Hotel'} was saved locally with five simulated nights.`
  } catch (requestError) {
    storageError.value = requestError.message || 'The hotel could not be saved locally. Please try again.'
  } finally {
    activeHotelId.value = ''
    activeHotelAction.value = ''
  }
}

async function removeHotel(hotel) {
  storageError.value = ''
  storageMessage.value = ''
  activeHotelId.value = hotel.place_id
  activeHotelAction.value = 'remove'

  try {
    await removeSavedHotel(hotel.place_id)
    const remainingIds = new Set(savedPlaceIds.value)
    remainingIds.delete(hotel.place_id)
    savedPlaceIds.value = remainingIds
    hotels.value = hotels.value.filter((item) => item.place_id !== hotel.place_id)
    if (selectedPlaceId.value === hotel.place_id) {
      selectedPlaceId.value = hotels.value[0]?.place_id || ''
    }
    storageMessage.value = `${hotel.name || 'Hotel'} was removed from local storage.`
  } catch (requestError) {
    storageError.value = requestError.message || 'The saved hotel could not be removed. Please try again.'
  } finally {
    activeHotelId.value = ''
    activeHotelAction.value = ''
  }
}

onMounted(refreshSavedStatus)
</script>

<template>
  <section class="nearby-search" aria-labelledby="nearby-search-title">
    <div class="nearby-search-heading">
      <p class="eyebrow section-eyebrow">Assignment 2 Part 2</p>
      <h2 id="nearby-search-title">Find hotels near a U.S. ZIP code</h2>
      <p class="section-intro">
        Search locally saved hotels first, then use live provider data only when no saved matches exist.
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
          :disabled="isBusy"
        />
      </div>
      <button type="submit" :disabled="isBusy" :aria-busy="isLoading">
        {{ isLoading ? 'Checking saved and nearby hotels…' : 'Search nearby hotels' }}
      </button>
    </form>

    <div class="nearby-feedback" aria-live="polite" aria-atomic="true">
      <p v-if="isLoading">Checking local storage before requesting live hotel data…</p>
      <p v-else-if="error" class="error-message">{{ error }}</p>
      <p v-else-if="searchCompleted && hotels.length === 0" class="empty-message">
        No hotels remain in the current results. Search again to check local storage and the live provider.
      </p>
      <p v-else-if="!searchCompleted" class="empty-message">
        Enter a ZIP code to find nearby hotels.
      </p>
    </div>

    <div class="local-hotel-feedback" aria-live="polite" aria-atomic="true">
      <p v-if="storageError" class="error-message">{{ storageError }}</p>
      <p v-else-if="storageMessage" class="success-message">{{ storageMessage }}</p>
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
      <div class="nearby-result-summary">
        <strong class="result-source-label">
          {{ resultSource === 'local' ? 'Saved locally' : 'API results' }}
        </strong>
        <p v-if="resultSource === 'local'">
          {{ hotels.length }} saved {{ hotels.length === 1 ? 'hotel' : 'hotels' }} found for
          {{ searchedZipCode }}. This saved subset is not a complete list of hotels in the area.
          Dates, rates, and rooms shown below are simulated classroom data.
        </p>
        <p v-else>
          {{ hotels.length }} {{ hotels.length === 1 ? 'hotel' : 'hotels' }} returned by Geoapify.
          Results include up to {{ resultLimit }} hotels within {{ radiusKilometers }} km of the resolved point.
        </p>
      </div>

      <div class="nearby-results-layout">
        <div class="nearby-hotel-list" aria-label="Nearby hotel results">
          <article
            v-for="(hotel, index) in hotels"
            :key="hotel.place_id"
            class="nearby-hotel-card"
            :class="{ 'nearby-hotel-selected': hotel.place_id === selectedPlaceId }"
          >
            <button
              type="button"
              class="nearby-hotel-selection"
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

            <div v-if="resultSource === 'local'" class="demo-night-panel">
              <p><strong>Simulated classroom stay data</strong></p>
              <div class="demo-night-table-wrap">
                <table class="demo-night-table">
                  <thead>
                    <tr>
                      <th scope="col">Date</th>
                      <th scope="col">Nightly rate</th>
                      <th scope="col">Rooms</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="night in hotel.nights" :key="night.stay_date">
                      <td>{{ night.stay_date }}</td>
                      <td>{{ nightlyRateLabel(night.nightly_rate_cents) }}</td>
                      <td>{{ night.rooms_available }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div class="local-hotel-actions">
              <button
                type="button"
                class="secondary-button"
                :disabled="isBusy || isSaved(hotel.place_id)"
                @click="addHotel(hotel)"
              >
                {{
                  activeHotelId === hotel.place_id && activeHotelAction === 'save'
                    ? 'Saving…'
                    : isSaved(hotel.place_id)
                      ? 'Saved locally'
                      : 'Add to Local'
                }}
              </button>
              <button
                v-if="isSaved(hotel.place_id)"
                type="button"
                class="danger-button"
                :disabled="isBusy"
                @click="removeHotel(hotel)"
              >
                {{
                  activeHotelId === hotel.place_id && activeHotelAction === 'remove'
                    ? 'Removing…'
                    : 'Remove from Local'
                }}
              </button>
            </div>
          </article>
          <p class="geoapify-attribution">
            {{ resultSource === 'local' ? 'Stored hotel identity and location data: Powered by Geoapify' : 'Hotel data: Powered by Geoapify' }}
          </p>
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
