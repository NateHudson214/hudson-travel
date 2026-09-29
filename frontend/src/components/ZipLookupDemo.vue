<script setup>
import { ref } from 'vue'

import { lookupDemoZipLocation, lookupZipLocation } from '../api/location.js'

const demoLocation = ref(null)
const demoError = ref('')
const enteredZipCode = ref('')
const enteredLocation = ref(null)
const enteredError = ref('')
const activeLookup = ref('')

async function handleLookup() {
  demoLocation.value = null
  demoError.value = ''
  activeLookup.value = 'demo'

  try {
    demoLocation.value = await lookupDemoZipLocation()
  } catch (requestError) {
    demoError.value = requestError.message || 'ZIP 16802 could not be looked up. Please try again.'
  } finally {
    activeLookup.value = ''
  }
}

async function handleEnteredLookup() {
  enteredLocation.value = null
  enteredError.value = ''

  const normalizedZipCode = enteredZipCode.value.trim()
  if (!/^[0-9]{5}$/.test(normalizedZipCode)) {
    enteredError.value = 'Enter a five-digit U.S. ZIP code.'
    return
  }

  activeLookup.value = 'entered'

  try {
    enteredLocation.value = await lookupZipLocation(normalizedZipCode)
  } catch (requestError) {
    enteredError.value = requestError.message || 'The ZIP code could not be looked up. Please try again.'
  } finally {
    activeLookup.value = ''
  }
}
</script>

<template>
  <section class="zip-demo" aria-labelledby="zip-demo-title">
    <div>
      <p class="eyebrow section-eyebrow">Assignment 2 demonstration</p>
      <h2 id="zip-demo-title">ZIP lookup demonstration</h2>
      <p class="section-intro">
        Ask the Hudson Travel backend to resolve the fixed ZIP code 16802.
      </p>
      <button
        type="button"
        :disabled="Boolean(activeLookup)"
        :aria-busy="activeLookup === 'demo'"
        @click="handleLookup"
      >
        {{ activeLookup === 'demo' ? 'Looking up ZIP 16802…' : 'Look up ZIP 16802' }}
      </button>
    </div>

    <div class="zip-demo-feedback" aria-live="polite" aria-atomic="true">
      <p v-if="activeLookup === 'demo'">Loading location…</p>
      <p v-else-if="demoError" class="error-message">{{ demoError }}</p>
      <dl v-else-if="demoLocation" class="location-details">
        <div>
          <dt>Postcode</dt>
          <dd>{{ demoLocation.postcode }}</dd>
        </div>
        <div v-if="demoLocation.locality">
          <dt>Locality</dt>
          <dd>{{ demoLocation.locality }}</dd>
        </div>
        <div>
          <dt>Latitude</dt>
          <dd>{{ demoLocation.latitude }}</dd>
        </div>
        <div>
          <dt>Longitude</dt>
          <dd>{{ demoLocation.longitude }}</dd>
        </div>
      </dl>
      <p v-else class="empty-message">Location details will appear here.</p>
    </div>

    <form class="zip-entry-form" novalidate @submit.prevent="handleEnteredLookup">
      <div class="input-group">
        <label for="zip-code">ZIP code</label>
        <input
          id="zip-code"
          v-model="enteredZipCode"
          name="zip-code"
          type="text"
          inputmode="numeric"
          autocomplete="off"
          placeholder="Enter five digits"
          :disabled="Boolean(activeLookup)"
        />
      </div>
      <button type="submit" :disabled="Boolean(activeLookup)" :aria-busy="activeLookup === 'entered'">
        {{ activeLookup === 'entered' ? 'Looking up ZIP…' : 'Look up entered ZIP' }}
      </button>
    </form>

    <div class="entered-zip-feedback" aria-live="polite" aria-atomic="true">
      <p v-if="activeLookup === 'entered'">Loading entered ZIP location…</p>
      <p v-else-if="enteredError" class="error-message">{{ enteredError }}</p>
      <div v-else-if="enteredLocation" class="table-wrap zip-table-wrap">
        <table>
          <thead>
            <tr>
              <th scope="col">ZIP code</th>
              <th scope="col">Locality</th>
              <th scope="col">Country code</th>
              <th scope="col">Latitude</th>
              <th scope="col">Longitude</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{{ enteredLocation.postcode }}</td>
              <td>{{ enteredLocation.locality || 'Not provided' }}</td>
              <td>{{ enteredLocation.country_code }}</td>
              <td>{{ enteredLocation.latitude }}</td>
              <td>{{ enteredLocation.longitude }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="empty-message">Enter a ZIP code to display its location in the table.</p>
    </div>
  </section>
</template>
