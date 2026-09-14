<script setup>
import { computed, onMounted, ref } from 'vue'

import {
  cancelBooking,
  createBooking,
  deleteBooking,
  loadBookings,
  loadUsers,
} from './api/bookings'
import { searchTrips } from './api/trips'
import BookingForm from './components/BookingForm.vue'
import BookingHistory from './components/BookingHistory.vue'
import StayResultsTable from './components/StayResultsTable.vue'
import StaySearch from './components/StaySearch.vue'

const trips = ref([])
const error = ref('')
const isLoading = ref(false)
const searchedHotelName = ref('')
const users = ref([])
const bookings = ref([])
const bookingError = ref('')
const bookingMessage = ref('')
const isBookingDataLoading = ref(false)
const bookingAction = ref('')
const activeBookingId = ref('')

const isBookingBusy = computed(
  () => isBookingDataLoading.value || Boolean(bookingAction.value),
)

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

async function refreshBookingData() {
  bookingError.value = ''
  isBookingDataLoading.value = true

  try {
    const [loadedUsers, loadedBookings] = await Promise.all([loadUsers(), loadBookings()])
    users.value = loadedUsers
    bookings.value = loadedBookings
  } catch (requestError) {
    bookingError.value = requestError.message || 'Booking data could not be loaded. Please try again.'
  } finally {
    isBookingDataLoading.value = false
  }
}

async function refreshHistoryAfterChange() {
  bookings.value = await loadBookings()
}

async function handleCreateBooking({ userId, tripId }) {
  bookingError.value = ''
  bookingMessage.value = ''

  if (!userId || !tripId) {
    bookingError.value = 'Select both a traveler and an offered stay before creating a booking.'
    return
  }

  bookingAction.value = 'create'
  let changeSaved = false

  try {
    const created = await createBooking(userId, tripId)
    changeSaved = true
    await refreshHistoryAfterChange()
    bookingMessage.value = `Booking ${created.booking_id} was created and added to history.`
  } catch (requestError) {
    bookingError.value = changeSaved
      ? 'The booking was saved, but history could not be refreshed. Refresh booking history to confirm it.'
      : requestError.message || 'Booking could not be created. Please try again.'
  } finally {
    bookingAction.value = ''
  }
}

async function handleCancelBooking(bookingId) {
  bookingError.value = ''
  bookingMessage.value = ''
  bookingAction.value = 'cancel'
  activeBookingId.value = bookingId
  let changeSaved = false

  try {
    await cancelBooking(bookingId)
    changeSaved = true
    await refreshHistoryAfterChange()
    bookingMessage.value = `Booking ${bookingId} was cancelled and remains in history.`
  } catch (requestError) {
    bookingError.value = changeSaved
      ? 'The cancellation was saved, but history could not be refreshed. Refresh booking history to confirm it.'
      : requestError.message || 'Booking could not be cancelled. Please try again.'
  } finally {
    bookingAction.value = ''
    activeBookingId.value = ''
  }
}

async function handleDeleteBooking(bookingId) {
  bookingError.value = ''
  bookingMessage.value = ''
  bookingAction.value = 'delete'
  activeBookingId.value = bookingId
  let changeSaved = false

  try {
    await deleteBooking(bookingId)
    changeSaved = true
    await refreshHistoryAfterChange()
    bookingMessage.value = `Booking ${bookingId} was deleted.`
  } catch (requestError) {
    bookingError.value = changeSaved
      ? 'The deletion was saved, but history could not be refreshed. Refresh booking history to confirm it.'
      : requestError.message || 'Booking could not be deleted. Please try again.'
  } finally {
    bookingAction.value = ''
    activeBookingId.value = ''
  }
}

function handleManualRefresh() {
  bookingMessage.value = ''
  refreshBookingData()
}

onMounted(refreshBookingData)
</script>

<template>
  <main class="page-shell">
    <section class="travel-card" aria-labelledby="page-title">
      <header class="hero">
        <p class="eyebrow">Hudson Travel</p>
        <h1 id="page-title">Find an offered stay</h1>
        <p class="intro">Search offered stays, create simulated bookings, and manage booking history.</p>
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

      <section class="booking-section" aria-labelledby="create-booking-title">
        <div class="section-heading">
          <div>
            <p class="eyebrow section-eyebrow">Part 2</p>
            <h2 id="create-booking-title">Create a simulated booking</h2>
          </div>
        </div>
        <p class="section-intro">Choose a traveler and one offered stay from the current search results.</p>
        <BookingForm
          :users="users"
          :trips="trips"
          :is-busy="isBookingBusy"
          @book="handleCreateBooking"
        />

        <div class="booking-feedback" aria-live="polite" aria-atomic="true">
          <p v-if="bookingError" class="error-message">{{ bookingError }}</p>
          <p v-else-if="bookingMessage" class="success-message">{{ bookingMessage }}</p>
        </div>
      </section>

      <section class="booking-section history-section" aria-labelledby="booking-history-title">
        <div class="section-heading">
          <div>
            <p class="eyebrow section-eyebrow">Saved in SQLite</p>
            <h2 id="booking-history-title">Booking history</h2>
          </div>
          <button
            type="button"
            class="secondary-button"
            :disabled="isBookingBusy"
            @click="handleManualRefresh"
          >
            {{ isBookingDataLoading ? 'Refreshing…' : 'Refresh history' }}
          </button>
        </div>

        <p v-if="isBookingDataLoading && bookings.length === 0" class="history-state">
          Loading booking history…
        </p>
        <p
          v-else-if="!isBookingDataLoading && !bookingError && bookings.length === 0"
          class="history-state empty-message"
        >
          No bookings are currently saved.
        </p>
        <BookingHistory
          v-else
          :bookings="bookings"
          :is-busy="isBookingBusy"
          :active-booking-id="activeBookingId"
          @cancel="handleCancelBooking"
          @delete="handleDeleteBooking"
        />
      </section>
    </section>
  </main>
</template>
