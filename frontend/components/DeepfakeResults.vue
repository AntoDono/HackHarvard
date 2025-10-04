<template>
  <div class="bg-white rounded-3xl shadow-2xl p-8 border-4 border-red-500">
    <!-- Alert Header -->
    <div class="text-center mb-8">
      <div class="inline-flex items-center justify-center w-24 h-24 bg-red-100 rounded-full mb-4 animate-pulse">
        <span class="text-5xl">🤖</span>
      </div>
      <h2 class="text-4xl font-bold text-red-600 mb-3">
        AI-Generated Content Detected
      </h2>
      <p class="text-xl text-gray-700 mb-2">{{ deepfakeData.message }}</p>
      <div class="inline-block px-6 py-2 bg-red-100 text-red-800 rounded-full font-semibold text-lg">
        {{ (deepfakeData.probability * 100).toFixed(1) }}% AI-Generated Probability
      </div>
    </div>

    <!-- Warning Message -->
    <div class="bg-red-50 border-l-4 border-red-500 p-6 rounded-xl mb-8">
      <div class="flex items-start">
        <span class="text-3xl mr-3">⚠️</span>
        <div>
          <h3 class="font-bold text-red-900 text-lg mb-2">Warning</h3>
          <p class="text-red-800">{{ deepfakeData.warning }}</p>
        </div>
      </div>
    </div>

    <!-- Confidence Level -->
    <div class="mb-8">
      <h3 class="text-xl font-semibold text-gray-900 mb-4">📊 Detection Confidence</h3>
      <div class="flex items-center gap-4">
        <div class="flex-1 bg-gray-200 rounded-full h-6 overflow-hidden">
          <div 
            class="h-full rounded-full transition-all duration-1000 ease-out"
            :class="confidenceBarColor"
            :style="{ width: `${deepfakeData.probability * 100}%` }"
          ></div>
        </div>
        <span class="text-lg font-bold" :class="confidenceTextColor">
          {{ confidenceLevelText }}
        </span>
      </div>
    </div>

    <!-- Model Results -->
    <div class="mb-8">
      <h3 class="text-xl font-semibold text-gray-900 mb-4">🔬 Individual Model Results</h3>
      <p class="text-sm text-gray-600 mb-4">Results from {{ deepfakeData.per_model_results.length }} different AI detection models:</p>
      
      <div class="space-y-3">
        <div 
          v-for="(model, index) in deepfakeData.per_model_results" 
          :key="index"
          class="bg-gray-50 rounded-xl p-4 border border-gray-200 hover:border-purple-300 transition-all"
        >
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-3">
              <span class="text-2xl">{{ model.detected_as_fake ? '🚨' : '✅' }}</span>
              <span class="font-semibold text-gray-900">{{ model.model }}</span>
            </div>
            <span 
              class="px-3 py-1 rounded-full text-sm font-bold"
              :class="model.detected_as_fake ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'"
            >
              {{ (model.probability * 100).toFixed(1) }}%
            </span>
          </div>
          <div class="bg-white rounded-lg h-2 overflow-hidden">
            <div 
              class="h-full transition-all duration-500"
              :class="model.detected_as_fake ? 'bg-red-500' : 'bg-green-500'"
              :style="{ width: `${model.probability * 100}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Average Score -->
    <div class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border-2 border-purple-200 mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-purple-900 mb-1">📈 Average Detection Score</h3>
          <p class="text-sm text-gray-600">Combined result from all models</p>
        </div>
        <div class="text-right">
          <div class="text-3xl font-bold text-purple-600">
            {{ (deepfakeData.average_probability * 100).toFixed(1) }}%
          </div>
          <div class="text-sm text-gray-600">AI-Generated</div>
        </div>
      </div>
    </div>

    <!-- Info Section -->
    <div class="bg-blue-50 border-l-4 border-blue-500 p-6 rounded-xl mb-8">
      <div class="flex items-start">
        <span class="text-2xl mr-3">💡</span>
        <div>
          <h3 class="font-bold text-blue-900 text-lg mb-2">What does this mean?</h3>
          <ul class="text-blue-800 space-y-2 text-sm">
            <li>• This image was likely created or significantly manipulated by AI technology</li>
            <li>• Multiple detection models analyzed different aspects of the image</li>
            <li>• The content may not represent real events, people, or products</li>
            <li>• Exercise caution when sharing or using this image</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex flex-col sm:flex-row gap-4 justify-center pt-4">
      <button 
        @click="$emit('reset')"
        class="flex-1 sm:flex-none px-8 py-4 bg-purple-600 text-white text-lg font-semibold rounded-full hover:bg-purple-700 transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-xl"
      >
        🔄 Try Another Image
      </button>
      <button 
        @click="downloadReport"
        class="flex-1 sm:flex-none px-8 py-4 bg-white text-purple-600 border-2 border-purple-600 text-lg font-semibold rounded-full hover:bg-purple-50 transition-all duration-300"
      >
        📥 Download Report
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  deepfakeData: {
    type: Object,
    required: true
  }
})

defineEmits(['reset'])

const confidenceBarColor = computed(() => {
  const prob = props.deepfakeData.probability
  if (prob > 0.75) return 'bg-red-500'
  if (prob > 0.5) return 'bg-orange-500'
  return 'bg-yellow-500'
})

const confidenceTextColor = computed(() => {
  const prob = props.deepfakeData.probability
  if (prob > 0.75) return 'text-red-600'
  if (prob > 0.5) return 'text-orange-600'
  return 'text-yellow-600'
})

const confidenceLevelText = computed(() => {
  const level = props.deepfakeData.confidence_level
  if (level === 'high') return 'HIGH'
  if (level === 'medium') return 'MEDIUM'
  return 'LOW'
})

const downloadReport = () => {
  const report = {
    timestamp: new Date().toISOString(),
    detection: 'AI-Generated Content',
    probability: props.deepfakeData.probability,
    confidence_level: props.deepfakeData.confidence_level,
    average_probability: props.deepfakeData.average_probability,
    per_model_results: props.deepfakeData.per_model_results,
    message: props.deepfakeData.message,
    warning: props.deepfakeData.warning
  }
  
  const dataStr = JSON.stringify(report, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `deepfake-detection-report-${Date.now()}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
