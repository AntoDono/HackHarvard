<template>
  <div class="mt-8 mx-4 bg-white rounded-3xl shadow-2xl overflow-hidden p-6 md:p-8">
    <h2 class="text-3xl font-bold text-gray-900 mb-6">✨ Detection Results</h2>
    
    <!-- Product Popout Card -->
    <div v-if="productImage || productUrl" class="mb-6 p-6 bg-gradient-to-br from-purple-50 via-pink-50 to-purple-50 rounded-2xl border-2 border-purple-200 shadow-lg">
      <div class="flex flex-col md:flex-row gap-6 items-center">
        <!-- Product Image -->
        <div v-if="productImage" class="flex-shrink-0">
          <img 
            :src="productImage" 
            :alt="item"
            class="w-32 h-32 md:w-40 md:h-40 object-cover rounded-xl shadow-md border-2 border-white"
          />
        </div>
        
        <!-- Product Info -->
        <div class="flex-1 text-center md:text-left">
          <h3 class="text-xl font-semibold text-purple-900 mb-2">🔍 Product Found</h3>
          <p class="text-2xl font-bold text-purple-600 mb-3">{{ item }}</p>
          
          <!-- Price Range -->
          <div v-if="priceRange && (priceRange[0] > 0 || priceRange[1] > 0)" class="mb-3">
            <p class="text-lg font-semibold text-gray-700">
              💰 Price Range: 
              <span class="text-green-600">
                ${{ priceRange[0].toFixed(2) }} - ${{ priceRange[1].toFixed(2) }}
              </span>
            </p>
          </div>
          
          <a 
            v-if="productUrl" 
            :href="productUrl" 
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white font-semibold rounded-full hover:bg-purple-700 transition-all shadow-md hover:shadow-lg"
          >
            <span>🌐 View Product Page</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>
      </div>
      <p class="text-xs text-gray-500 mt-4 text-center">Detection ID: {{ detectionId }}</p>
    </div>
    
    <!-- Item Info (fallback if no product image/url) -->
    <div v-else class="mb-6 p-6 bg-purple-50 rounded-2xl">
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
  locationAngles: Array,
  productImage: String,
  productUrl: String,
  priceRange: Array
})

defineEmits(['continue', 'reset'])
</script>

