<script setup>
defineProps({
  trips: {
    type: Array,
    required: true,
  },
})

const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
})
</script>

<template>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th scope="col">Trip</th>
          <th scope="col">Hotel</th>
          <th scope="col">City</th>
          <th scope="col">State</th>
          <th scope="col">Check-in</th>
          <th scope="col">Check-out</th>
          <th scope="col" class="numeric">Nightly rate</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="trip in trips" :key="trip.trip_id">
          <td>{{ trip.trip_id }} — {{ trip.trip_name }}</td>
          <td>{{ trip.hotel_name }}</td>
          <td>{{ trip.city }}</td>
          <td>{{ trip.state }}</td>
          <td>{{ trip.check_in }}</td>
          <td>{{ trip.check_out }}</td>
          <td class="numeric">{{ currencyFormatter.format(trip.nightly_rate_usd) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
