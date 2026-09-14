<script setup>
defineProps({
  bookings: {
    type: Array,
    required: true,
  },
  isBusy: {
    type: Boolean,
    default: false,
  },
  activeBookingId: {
    type: String,
    default: '',
  },
})

defineEmits(['cancel', 'delete'])
</script>

<template>
  <div class="table-wrap booking-table-wrap">
    <table>
      <thead>
        <tr>
          <th scope="col">Booking</th>
          <th scope="col">Traveler</th>
          <th scope="col">Trip</th>
          <th scope="col">Hotel</th>
          <th scope="col">Stay dates</th>
          <th scope="col">Booked on</th>
          <th scope="col">Status</th>
          <th scope="col">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="booking in bookings" :key="booking.booking_id">
          <td>{{ booking.booking_id }}</td>
          <td>{{ booking.user_id }} — {{ booking.display_name }}</td>
          <td>{{ booking.trip_id }} — {{ booking.trip_name }}</td>
          <td>{{ booking.hotel_name }}</td>
          <td>{{ booking.check_in }} to {{ booking.check_out }}</td>
          <td>{{ booking.booked_on }}</td>
          <td>
            <span class="status-badge" :class="`status-${booking.status}`">
              {{ booking.status }}
            </span>
          </td>
          <td>
            <div class="row-actions">
              <button
                v-if="booking.status === 'confirmed'"
                type="button"
                class="secondary-button"
                :disabled="isBusy"
                @click="$emit('cancel', booking.booking_id)"
              >
                {{ activeBookingId === booking.booking_id ? 'Working…' : 'Cancel' }}
              </button>
              <button
                type="button"
                class="danger-button"
                :disabled="isBusy"
                @click="$emit('delete', booking.booking_id)"
              >
                {{ activeBookingId === booking.booking_id ? 'Working…' : 'Delete' }}
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
