<template>
  <div class="mt-8 mx-4 bg-white rounded-3xl shadow-2xl overflow-hidden p-6 md:p-8">
    <h2 class="text-3xl font-bold text-gray-900 mb-6">✨ Detection Results</h2>
    
    <!-- Item Info -->
    <div class="mb-6 p-6 bg-purple-50 rounded-2xl">
      <h3 class="text-xl font-semibold text-purple-900 mb-2">Detected Item</h3>
      <p class="text-2xl font-bold text-purple-600">{{ item }}</p>
      <p class="text-sm text-gray-600 mt-2">Detection ID: {{ detectionId }}</p>
    </div>

    <!-- Camera Instructions -->
    <div class="mb-6">
      <h3 class="text-xl font-semibold text-gray-900 mb-4">📸 Next Steps: Capture These Views</h3>
      <p class="text-gray-600 mb-4">Please take photos of the following angles to verify authenticity:</p>
      
      <div class="space-y-4">
        <div 
          v-for="(location, index) in locationAngles" 
          :key="index"
          class="p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border-l-4 border-purple-500"
        >
          <div class="flex items-start gap-3">
            <div class="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold">
              {{ index + 1 }}
            </div>
            <div class="flex-1">
              <p class="font-semibold text-gray-900">
                📷 {{ location }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex gap-4 justify-center">
      <button 
        @click="$emit('continue')"
        class="px-8 py-4 bg-purple-600 text-white text-lg font-semibold rounded-full hover:bg-purple-700 transition-all duration-300 hover:scale-105 shadow-lg"
      >
        📸 Continue to Capture
      </button>
      <button 
        @click="$emit('reset')"
        class="px-8 py-4 bg-white text-purple-600 border-2 border-purple-600 text-lg font-semibold rounded-full hover:bg-purple-50 transition-all duration-300"
      >
        🔄 Start Over
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  item: String,
  detectionId: String,
  locationAngles: Array
})

defineEmits(['continue', 'reset'])
</script>

