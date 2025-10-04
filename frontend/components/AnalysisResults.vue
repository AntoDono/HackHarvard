<template>
  <div class="mt-8 mx-4 bg-white rounded-3xl shadow-2xl overflow-hidden p-6 md:p-8">
    <h2 class="text-4xl font-bold text-center mb-8">
      <span v-if="result.is_authentic" class="text-green-600">✓ Authentic</span>
      <span v-else class="text-red-600">✗ Counterfeit</span>
    </h2>

    <!-- Overall Confidence -->
    <div class="mb-6 p-6 bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl text-center">
      <p class="text-sm text-gray-600 mb-2">Overall Confidence</p>
      <p class="text-4xl font-bold text-purple-600">{{ (result.overall_confidence * 100).toFixed(1) }}%</p>
    </div>

    <!-- Summary -->
    <div class="mb-6 p-6 bg-gray-50 rounded-2xl">
      <h3 class="text-xl font-semibold text-gray-900 mb-3">Summary</h3>
      <p class="text-gray-700">{{ result.summary }}</p>
    </div>

    <!-- Criteria Results -->
    <div class="mb-6">
      <h3 class="text-xl font-semibold text-gray-900 mb-4">Detailed Results</h3>
      <div class="space-y-3">
        <div 
          v-for="(criterionResult, index) in result.criteria_results" 
          :key="index"
          :class="[
            'p-4 rounded-xl border-l-4',
            criterionResult.passed ? 'bg-green-50 border-green-500' : 'bg-red-50 border-red-500'
          ]"
        >
          <div class="flex items-start gap-3">
            <div class="flex-shrink-0">
              <span v-if="criterionResult.passed" class="text-2xl">✓</span>
              <span v-else class="text-2xl">✗</span>
            </div>
            <div class="flex-1">
              <p class="font-semibold text-gray-900 mb-1">{{ criterionResult.criterion }}</p>
              <p class="text-sm text-gray-600 mb-2">{{ criterionResult.notes }}</p>
              <p class="text-xs text-gray-500">Confidence: {{ (criterionResult.confidence * 100).toFixed(1) }}%</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex gap-4 justify-center">
      <button 
        @click="$emit('reset')"
        class="px-8 py-4 bg-purple-600 text-white text-lg font-semibold rounded-full hover:bg-purple-700 transition-all duration-300 hover:scale-105 shadow-lg"
      >
        🔄 Check Another Item
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  result: {
    type: Object,
    required: true
  }
})

defineEmits(['reset'])
</script>

