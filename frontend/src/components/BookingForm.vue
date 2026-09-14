<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  users: {
    type: Array,
    required: true,
  },
  trips: {
    type: Array,
    required: true,
  },
  isBusy: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['book'])
const userId = ref('')
const tripId = ref('')

watch(
  () => props.trips,
  (availableTrips) => {
    if (!availableTrips.some((trip) => trip.trip_id === tripId.value)) {
      tripId.value = ''
    }
  },
)

function submitBooking() {
  emit('book', { userId: userId.value, tripId: tripId.value })
}
</script>

<template>
  <form class="booking-form" novalidate @submit.prevent="submitBooking">
    <div class="input-group">
      <label for="traveler">Traveler</label>
      <select id="traveler" v-model="userId" :disabled="isBusy">
        <option value="">Select a traveler</option>
        <option v-for="user in users" :key="user.user_id" :value="user.user_id">
          {{ user.user_id }} — {{ user.display_name }}
        </option>
      </select>
    </div>

    <div class="input-group">
      <label for="offered-stay">Offered stay from current search</label>
      <select id="offered-stay" v-model="tripId" :disabled="isBusy || trips.length === 0">
        <option value="">{{ trips.length ? 'Select an offered stay' : 'Search for a hotel first' }}</option>
        <option v-for="trip in trips" :key="trip.trip_id" :value="trip.trip_id">
          {{ trip.trip_id }} — {{ trip.trip_name }} at {{ trip.hotel_name }}
        </option>
      </select>
    </div>

    <button type="submit" :disabled="isBusy">
      {{ isBusy ? 'Please wait…' : 'Create booking' }}
    </button>
  </form>
</template>
