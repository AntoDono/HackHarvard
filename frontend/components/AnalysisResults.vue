<template>
  <div class="mt-8 mx-4 bg-white rounded-3xl shadow-2xl overflow-hidden p-6 md:p-8">
    <h2 class="text-4xl font-bold text-center mb-8">
      <span v-if="result.is_authentic" class="text-green-600">✓ Authentic</span>
      <span v-else class="text-red-600">✗ Counterfeit</span>
    </h2>

    <!-- Initial Scan Results -->
    <div v-if="result.initial_scan" class="mb-8 p-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl border-2 border-indigo-200">
      <h3 class="text-xl font-semibold text-gray-900 mb-4">🔍 Initial Scan Analysis</h3>
      <p class="text-sm text-gray-600 mb-4">Comparing your item with the reference product image</p>
      
      <!-- Product Info Card -->
      <div v-if="productImage || productUrl" class="mb-6 p-4 bg-white rounded-xl shadow-md border border-indigo-200">
        <div class="flex flex-col md:flex-row gap-4 items-center">
          <!-- Product Image -->
          <div v-if="productImage" class="flex-shrink-0">
            <img 
              :src="productImage" 
              :alt="productName || 'Product'"
              class="w-32 h-32 object-cover rounded-lg shadow-sm border-2 border-indigo-200"
            />
          </div>
          
          <!-- Product Info -->
          <div class="flex-1 text-center md:text-left">
            <p v-if="productName" class="text-lg font-bold text-gray-900 mb-2">{{ productName }}</p>
            <a 
              v-if="productUrl" 
              :href="productUrl" 
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white font-semibold rounded-full hover:bg-indigo-700 transition-all shadow-sm hover:shadow-md text-sm"
            >
              <span>🌐 View Reference Product</span>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>
        </div>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-white rounded-xl p-4 text-center shadow-sm">
          <p class="text-3xl font-bold text-indigo-600">{{ (result.initial_scan.similarity_score * 100).toFixed(1) }}%</p>
          <p class="text-xs text-gray-600">Image Embedding Score</p>
        </div>
        <div class="bg-white rounded-xl p-4 text-center shadow-sm">
          <p class="text-lg font-bold" :class="productUrl ? 'text-green-600' : 'text-orange-600'">
            {{ productUrl ? 'MATCH' : 'NO MATCH' }}
          </p>
          <p class="text-xs text-gray-600">Match Status</p>
        </div>
        <div class="bg-white rounded-xl p-4 text-center shadow-sm">
          <p class="text-lg font-bold" :class="averageScore > 3 ? 'text-green-600' : 'text-orange-600'">
            {{ averageScore > 3.5 ? 'Confident' : 'Not Confident' }}
          </p>
          <p class="text-xs text-gray-600">Confidence</p>
        </div>
      </div>
    </div>


    <!-- Risk Assessment -->
    <div v-if="result.risk_assessment" class="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Overall Confidence -->
      <div class="p-6 bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl text-center">
        <p class="text-sm text-gray-600 mb-2">Overall Confidence</p>
        <p class="text-4xl font-bold text-purple-600">{{ (result.overall_confidence * 100).toFixed(1) }}%</p>
      </div>
      
      <!-- Risk Level -->
      <div class="p-6 rounded-2xl text-center" :class="getRiskBackground(result.risk_assessment.risk_level)">
        <p class="text-sm text-gray-600 mb-2">Risk Level</p>
        <p class="text-4xl font-bold capitalize" :class="getRiskColor(result.risk_assessment.risk_level)">
          {{ result.risk_assessment.risk_level }}
        </p>
        <p class="text-sm text-gray-600 mt-2">
          {{ result.risk_assessment.counterfeit_probability }}% counterfeit probability
        </p>
      </div>
    </div>

    <!-- Criteria Scores Summary -->
    <div class="mb-6 grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Executive Summary -->
      <div class="p-6 bg-gray-50 rounded-2xl">
        <h3 class="text-xl font-semibold text-gray-900 mb-3">Executive Summary</h3>
        <p class="text-gray-700 leading-relaxed">{{ result.summary }}</p>
      </div>
      
      <!-- Average and Individual Scores -->
      <div class="p-6 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl">
        <h3 class="text-xl font-semibold text-gray-900 mb-4">Criteria Scores</h3>
        
        <!-- Average Score -->
        <div class="mb-4 pb-4 border-b border-purple-200">
          <div class="flex items-center justify-between mb-2">
            <span class="text-lg font-semibold text-gray-700">Average Score</span>
            <span class="text-2xl font-bold" :class="getScoreColor(averageScore)">
              {{ averageScore.toFixed(1) }}/5
            </span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
            <div 
              class="h-full rounded-full transition-all duration-500 ease-out"
              :class="getScoreBarColor(averageScore)"
              :style="{ width: `${(averageScore / 5) * 100}%` }"
            ></div>
          </div>
        </div>
        
        <!-- Individual Criteria Scores -->
        <div class="space-y-3">
          <div v-for="(criterionResult, index) in result.criteria_results" :key="index">
            <div class="flex items-center justify-between mb-1">
              <span class="text-sm text-gray-600">Criteria {{ index + 1 }}</span>
              <span class="text-sm font-bold" :class="getScoreColor(criterionResult.score)">
                {{ criterionResult.score }}/5
              </span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
              <div 
                class="h-full rounded-full transition-all duration-500 ease-out"
                :class="getScoreBarColor(criterionResult.score)"
                :style="{ width: `${(criterionResult.score / 5) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Key Concerns -->
    <div v-if="result.risk_assessment?.key_concerns && result.risk_assessment.key_concerns.length > 0" 
         class="mb-6 p-6 bg-red-50 rounded-2xl border-2 border-red-200">
      <h3 class="text-xl font-semibold text-red-900 mb-4">🚩 Key Concerns</h3>
      <ul class="space-y-2">
        <li v-for="(concern, index) in result.risk_assessment.key_concerns" :key="index" 
            class="flex items-start gap-2">
          <span class="text-red-600 mt-1">•</span>
          <span class="text-red-900">{{ concern }}</span>
        </li>
      </ul>
    </div>

    <!-- Criteria Results -->
    <div class="mb-6">
      <h3 class="text-xl font-semibold text-gray-900 mb-4">Detailed Results</h3>
      <div class="space-y-4">
        <div 
          v-for="(criterionResult, index) in result.criteria_results" 
          :key="index"
          :class="[
            'p-5 rounded-xl border-l-4 shadow-sm',
            criterionResult.passed ? 'bg-green-50 border-green-500' : 'bg-red-50 border-red-500'
          ]"
        >
          <!-- Layout Grid -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Left: Criterion Image -->
            <div v-if="criteriaImages && criteriaImages[index]" class="md:col-span-1">
              <img 
                :src="criteriaImages[index]" 
                :alt="`Criterion ${index + 1} image`"
                class="w-full h-48 object-cover rounded-lg shadow-md border-2"
                :class="criterionResult.passed ? 'border-green-300' : 'border-red-300'"
              />
              <p class="text-xs text-gray-500 text-center mt-2">Captured Image {{ index + 1 }}</p>
            </div>
            
            <!-- Right: Stats and Assessment -->
            <div :class="criteriaImages && criteriaImages[index] ? 'md:col-span-2' : 'md:col-span-3'">
              <!-- Top: Criterion Name & Stats -->
              <div class="mb-4">
                <!-- Criterion Name -->
                <div class="flex items-start gap-2 mb-3">
                  <span :class="[
                    'text-2xl flex-shrink-0',
                    criterionResult.passed ? 'text-green-600' : 'text-red-600'
                  ]">
                    {{ criterionResult.passed ? '✓' : '✗' }}
                  </span>
                  <div class="flex-1">
                    <p class="text-xs uppercase text-gray-500 mb-1">Criteria {{ index + 1 }}</p>
                    <p class="font-semibold text-gray-900 leading-tight break-words">{{ criterionResult.criterion }}</p>
                  </div>
                </div>
            
              <!-- Score Display -->
              <div class="mb-2">
                <div class="flex items-center justify-between mb-1">
                  <span class="text-sm font-medium text-gray-700">Score</span>
                  <span class="text-lg font-bold" :class="getScoreColor(criterionResult.score)">
                    {{ criterionResult.score }}/5
                  </span>
                </div>
                
                <!-- Progress Bar -->
                <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div 
                    class="h-full rounded-full transition-all duration-500 ease-out"
                    :class="getScoreBarColor(criterionResult.score)"
                    :style="{ width: `${(criterionResult.score / 5) * 100}%` }"
                  ></div>
                </div>
              </div>
              
              <!-- Confidence Percentage -->
              <div class="text-xs text-gray-600">
                Confidence: <span class="font-semibold">{{ criterionResult.confidence_percentage || (criterionResult.confidence * 100).toFixed(1) }}%</span>
              </div>
            </div>
            
              <!-- Bottom: Assessment Notes -->
              <div class="bg-white bg-opacity-50 rounded-lg p-3">
                <p class="text-xs uppercase font-semibold text-gray-500 mb-1">Assessment</p>
                <p class="text-sm text-gray-700 leading-relaxed break-words mb-2">{{ criterionResult.notes }}</p>
                
                <!-- Visual Markers -->
                <div v-if="criterionResult.visual_markers && criterionResult.visual_markers.length > 0" class="mb-2">
                  <p class="text-xs font-semibold text-gray-600 mb-1">Visual Markers:</p>
                  <div class="flex flex-wrap gap-1">
                    <span v-for="(marker, idx) in criterionResult.visual_markers" 
                          :key="idx"
                          class="px-2 py-1 bg-gray-200 text-xs rounded">
                      {{ marker }}
                    </span>
                  </div>
                </div>
                
                <!-- Comparison Notes -->
                <div v-if="criterionResult.comparison_notes" class="border-t pt-2 mt-2">
                  <p class="text-xs font-semibold text-gray-600 mb-1">Comparison:</p>
                  <p class="text-xs text-gray-600 italic">{{ criterionResult.comparison_notes }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recommendations -->
    <div v-if="result.recommendations && result.recommendations.length > 0" 
         class="mb-6 p-6 bg-blue-50 rounded-2xl border-2 border-blue-200">
      <h3 class="text-xl font-semibold text-blue-900 mb-4">💡 Recommendations</h3>
      <ul class="space-y-2">
        <li v-for="(recommendation, index) in result.recommendations" :key="index" 
            class="flex items-start gap-2">
          <span class="text-blue-600 mt-1">•</span>
          <span class="text-blue-900">{{ recommendation }}</span>
        </li>
      </ul>
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
import { computed } from 'vue'

const props = defineProps({
  result: {
    type: Object,
    required: true
  },
  criteriaImages: {
    type: Array,
    default: () => []
  },
  productName: {
    type: String,
    default: ''
  },
  productImage: {
    type: String,
    default: ''
  },
  productUrl: {
    type: String,
    default: ''
  }
})

defineEmits(['reset'])

// Computed property for average score
const averageScore = computed(() => {
  if (!props.result.criteria_results || props.result.criteria_results.length === 0) {
    return 0
  }
  const sum = props.result.criteria_results.reduce((acc, criterion) => acc + (criterion.score || 0), 0)
  return sum / props.result.criteria_results.length
})

// Helper function to get score color
const getScoreColor = (score) => {
  if (score >= 4) return 'text-green-600'
  if (score >= 3) return 'text-yellow-600'
  return 'text-red-600'
}

// Helper function to get progress bar color
const getScoreBarColor = (score) => {
  if (score >= 4) return 'bg-green-500'
  if (score >= 3) return 'bg-yellow-500'
  return 'bg-red-500'
}

// Helper function to get risk color
const getRiskColor = (level) => {
  const riskLevel = level?.toLowerCase() || 'unknown'
  if (riskLevel === 'low') return 'text-green-600'
  if (riskLevel === 'medium') return 'text-yellow-600'
  if (riskLevel === 'high') return 'text-orange-600'
  if (riskLevel === 'critical') return 'text-red-600'
  return 'text-gray-600'
}

// Helper function to get risk background
const getRiskBackground = (level) => {
  const riskLevel = level?.toLowerCase() || 'unknown'
  if (riskLevel === 'low') return 'bg-green-50'
  if (riskLevel === 'medium') return 'bg-yellow-50'
  if (riskLevel === 'high') return 'bg-orange-50'
  if (riskLevel === 'critical') return 'bg-red-50'
  return 'bg-gray-50'
}
</script>

