<script setup>
import * as L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  location: {
    type: Object,
    required: true,
  },
  hotels: {
    type: Array,
    required: true,
  },
  selectedPlaceId: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['select'])
const mapElement = ref(null)

let map
let searchCenterLayer
let hotelLayer
const markerRecords = new Map()

function hotelIcon(index, selected) {
  return L.divIcon({
    className: `hotel-marker${selected ? ' hotel-marker-selected' : ''}`,
    html: `<span>${index + 1}</span>`,
    iconSize: selected ? [36, 36] : [30, 30],
    iconAnchor: selected ? [18, 18] : [15, 15],
  })
}

function popupContent(hotel) {
  const content = document.createElement('div')
  const name = document.createElement('strong')
  const address = document.createElement('div')

  name.textContent = hotel.name || 'Name unavailable'
  address.textContent = hotel.formatted_address || 'Address unavailable'
  content.append(name, address)
  return content
}

function applySelection() {
  for (const [placeId, record] of markerRecords) {
    const selected = placeId === props.selectedPlaceId
    record.marker.setIcon(hotelIcon(record.index, selected))
    record.marker.setZIndexOffset(selected ? 1000 : 0)
    if (selected) {
      record.marker.openPopup()
    } else {
      record.marker.closePopup()
    }
  }
}

function renderResults() {
  if (!map || !searchCenterLayer || !hotelLayer) {
    return
  }

  searchCenterLayer.clearLayers()
  hotelLayer.clearLayers()
  markerRecords.clear()

  const center = [props.location.latitude, props.location.longitude]
  const boundsPoints = [center]

  L.circleMarker(center, {
    radius: 7,
    color: '#7c1723',
    fillColor: '#b42335',
    fillOpacity: 1,
    weight: 2,
  })
    .bindTooltip(`ZIP ${props.location.postcode} search center`)
    .addTo(searchCenterLayer)

  props.hotels.forEach((hotel, index) => {
    const point = [hotel.latitude, hotel.longitude]
    const marker = L.marker(point, {
      icon: hotelIcon(index, hotel.place_id === props.selectedPlaceId),
      keyboard: true,
      riseOnHover: true,
      title: hotel.name || 'Name unavailable',
    })
      .bindPopup(popupContent(hotel))
      .on('click', () => emit('select', hotel.place_id))
      .addTo(hotelLayer)

    markerRecords.set(hotel.place_id, { marker, index })
    boundsPoints.push(point)
  })

  map.fitBounds(L.latLngBounds(boundsPoints), {
    padding: [32, 32],
    maxZoom: 15,
  })
  applySelection()
}

onMounted(() => {
  map = L.map(mapElement.value, {
    scrollWheelZoom: false,
  })
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
  }).addTo(map)
  searchCenterLayer = L.layerGroup().addTo(map)
  hotelLayer = L.layerGroup().addTo(map)
  renderResults()
})

watch(
  () => [props.location, props.hotels],
  renderResults,
  { deep: true },
)
watch(() => props.selectedPlaceId, applySelection)

onBeforeUnmount(() => {
  markerRecords.clear()
  if (map) {
    map.remove()
  }
  map = undefined
  searchCenterLayer = undefined
  hotelLayer = undefined
})
</script>

<template>
  <div
    ref="mapElement"
    class="nearby-hotels-map"
    role="region"
    aria-label="Map of hotels near the resolved ZIP code"
  ></div>
</template>
