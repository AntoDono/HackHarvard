<template>
  <div class="mt-8 mx-4 bg-white rounded-3xl shadow-2xl overflow-hidden p-6 md:p-8">
    <h2 class="text-4xl font-bold text-center mb-8">
      <span class="text-purple-600">📋 Fact Check Results</span>
    </h2>

    <!-- Main Content -->
    <div class="w-full mx-auto flex flex-col gap-6">
      
      <!-- Overall Verdict Card -->
      <div class="p-6 rounded-2xl text-center" :class="getVerdictBackground(overallVerdict)">
        <p class="text-sm text-gray-600 mb-2">Overall Verdict</p>
        <p class="text-5xl font-bold mb-2" :class="getVerdictColor(overallVerdict)">
          {{ getVerdictIcon(overallVerdict) }} {{ overallVerdict }}
        </p>
        <p class="text-lg font-semibold text-gray-700 mb-4">
          Confidence: {{ (confidenceScore * 100).toFixed(0) }}%
        </p>
        <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div 
            class="h-full transition-all duration-500" 
            :class="getVerdictProgressColor(overallVerdict)"
            :style="{ width: (confidenceScore * 100) + '%' }"
          ></div>
        </div>
      </div>

      <!-- Image Type & Summary -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-purple-50 rounded-xl p-4 text-center">
          <p class="text-sm text-gray-600 mb-1">Content Type</p>
          <p class="text-2xl font-bold text-purple-600">{{ formatImageType(imageType) }}</p>
        </div>
        <div class="bg-blue-50 rounded-xl p-4 text-center">
          <p class="text-sm text-gray-600 mb-1">Claims Found</p>
          <p class="text-2xl font-bold text-blue-600">{{ claims.length }}</p>
        </div>
      </div>

      <!-- Summary -->
      <div class="p-6 bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl border-2 border-purple-200">
        <h3 class="text-xl font-semibold text-purple-900 mb-3">📝 Summary</h3>
        <p class="text-gray-700 leading-relaxed">{{ summary }}</p>
      </div>

      <!-- Important Notes (if any) -->
      <div v-if="importantNotes" class="p-6 bg-yellow-50 rounded-2xl border-2 border-yellow-300">
        <h3 class="text-xl font-semibold text-yellow-900 mb-3">⚠️ Important Notes</h3>
        <p class="text-gray-700 leading-relaxed">{{ importantNotes }}</p>
      </div>

      <!-- Individual Claims -->
      <div v-if="claims && claims.length > 0" class="space-y-4">
        <h3 class="text-2xl font-bold text-gray-900 mb-4">🔍 Detailed Claims Analysis</h3>
        
        <div 
          v-for="(claim, index) in claims" 
          :key="index"
          class="p-6 rounded-2xl border-2 transition-all hover:shadow-lg"
          :class="getClaimBorderColor(claim.verdict)"
        >
          <!-- Claim Header -->
          <div class="flex items-start gap-4 mb-4">
            <div class="flex-shrink-0 text-4xl">
              {{ getClaimIcon(claim.verdict) }}
            </div>
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <span 
                  class="px-3 py-1 rounded-full text-sm font-bold"
                  :class="getClaimBadgeClass(claim.verdict)"
                >
                  {{ claim.verdict }}
                </span>
                <span class="text-sm text-gray-500">
                  {{ formatClaimType(claim.claim_type) }}
                </span>
              </div>
              <p class="text-lg font-semibold text-gray-900 mb-2">
                "{{ claim.claim_text }}"
              </p>
              <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <div 
                  class="h-full transition-all"
                  :class="getClaimProgressColor(claim.verdict)"
                  :style="{ width: (claim.confidence * 100) + '%' }"
                ></div>
              </div>
              <p class="text-xs text-gray-500 mt-1">
                Confidence: {{ (claim.confidence * 100).toFixed(0) }}%
              </p>
            </div>
          </div>

          <!-- Evidence -->
          <div class="mb-4 p-4 bg-gray-50 rounded-xl">
            <h4 class="font-semibold text-gray-900 mb-2">📚 Evidence:</h4>
            <p class="text-gray-700 leading-relaxed">{{ claim.evidence }}</p>
          </div>

          <!-- Sources -->
          <div v-if="claim.sources && claim.sources.length > 0" class="mb-4">
            <h4 class="font-semibold text-gray-900 mb-2">🔗 Sources:</h4>
            <div class="space-y-2">
              <div 
                v-for="(source, sIndex) in claim.sources" 
                :key="sIndex"
                class="p-3 bg-white rounded-lg border border-gray-200 hover:border-purple-300 transition-all"
              >
                <div class="flex items-center justify-between gap-2">
                  <div class="flex-1">
                    <p class="font-medium text-gray-900 text-sm">{{ source.title }}</p>
                    <a 
                      v-if="source.url" 
                      :href="source.url" 
                      target="_blank"
                      rel="noopener noreferrer"
                      class="text-xs text-purple-600 hover:underline break-all"
                    >
                      {{ source.url }}
                    </a>
                  </div>
                  <span 
                    class="px-2 py-1 rounded-full text-xs font-semibold flex-shrink-0"
                    :class="getReliabilityBadgeClass(source.reliability)"
                  >
                    {{ source.reliability }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Context -->
          <div v-if="claim.context" class="p-4 bg-blue-50 rounded-xl">
            <h4 class="font-semibold text-blue-900 mb-2">💡 Context:</h4>
            <p class="text-gray-700 text-sm leading-relaxed">{{ claim.context }}</p>
          </div>
        </div>
      </div>

      <!-- No Claims Found -->
      <div v-else class="p-8 bg-gray-50 rounded-2xl text-center">
        <p class="text-xl text-gray-600">No factual claims were found in this content.</p>
        <p class="text-sm text-gray-500 mt-2">This may be an opinion piece, artwork, or other non-factual content.</p>
      </div>

      <!-- Reset Button -->
      <div class="flex justify-center mt-8">
        <button
          @click="$emit('reset')"
          class="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold text-lg rounded-full shadow-lg hover:shadow-xl transform hover:scale-105 transition-all"
        >
          🔄 Check Another Item
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  imageType: {
    type: String,
    default: 'unknown'
  },
  containsFactualClaims: {
    type: Boolean,
    default: false
  },
  overallVerdict: {
    type: String,
    default: 'UNVERIFIABLE'
  },
  confidenceScore: {
    type: Number,
    default: 0
  },
  claims: {
    type: Array,
    default: () => []
  },
  summary: {
    type: String,
    default: ''
  },
  importantNotes: {
    type: String,
    default: ''
  }
})

defineEmits(['reset'])

const formatImageType = (type) => {
  const types = {
    'tweet': '🐦 Tweet',
    'text_document': '📄 Text Document',
    'infographic': '📊 Infographic',
    'news': '📰 News',
    'meme': '🎭 Meme',
    'drawing': '🎨 Drawing',
    'other': '❓ Other'
  }
  return types[type] || type
}

const formatClaimType = (type) => {
  const types = {
    'statistical': '📊 Statistical',
    'historical': '📜 Historical',
    'scientific': '🔬 Scientific',
    'news': '📰 News',
    'quote': '💬 Quote',
    'other': '📝 General'
  }
  return types[type] || type
}

const getVerdictIcon = (verdict) => {
  const icons = {
    'TRUE': '✅',
    'FALSE': '❌',
    'PARTIALLY TRUE': '⚠️',
    'MOSTLY TRUE': '✓',
    'MOSTLY FALSE': '✗',
    'UNVERIFIABLE': '❓',
    'SATIRE/OPINION': '🎭'
  }
  return icons[verdict] || '❓'
}

const getClaimIcon = (verdict) => {
  const icons = {
    'TRUE': '✅',
    'FALSE': '❌',
    'PARTIALLY TRUE': '⚠️',
    'UNVERIFIABLE': '❓'
  }
  return icons[verdict] || '❓'
}

const getVerdictBackground = (verdict) => {
  const backgrounds = {
    'TRUE': 'bg-green-50 border-2 border-green-300',
    'FALSE': 'bg-red-50 border-2 border-red-300',
    'PARTIALLY TRUE': 'bg-yellow-50 border-2 border-yellow-300',
    'MOSTLY TRUE': 'bg-green-50 border-2 border-green-300',
    'MOSTLY FALSE': 'bg-orange-50 border-2 border-orange-300',
    'UNVERIFIABLE': 'bg-gray-50 border-2 border-gray-300',
    'SATIRE/OPINION': 'bg-purple-50 border-2 border-purple-300'
  }
  return backgrounds[verdict] || 'bg-gray-50 border-2 border-gray-300'
}

const getVerdictColor = (verdict) => {
  const colors = {
    'TRUE': 'text-green-600',
    'FALSE': 'text-red-600',
    'PARTIALLY TRUE': 'text-yellow-600',
    'MOSTLY TRUE': 'text-green-600',
    'MOSTLY FALSE': 'text-orange-600',
    'UNVERIFIABLE': 'text-gray-600',
    'SATIRE/OPINION': 'text-purple-600'
  }
  return colors[verdict] || 'text-gray-600'
}

const getVerdictProgressColor = (verdict) => {
  const colors = {
    'TRUE': 'bg-green-500',
    'FALSE': 'bg-red-500',
    'PARTIALLY TRUE': 'bg-yellow-500',
    'MOSTLY TRUE': 'bg-green-500',
    'MOSTLY FALSE': 'bg-orange-500',
    'UNVERIFIABLE': 'bg-gray-500',
    'SATIRE/OPINION': 'bg-purple-500'
  }
  return colors[verdict] || 'bg-gray-500'
}

const getClaimBorderColor = (verdict) => {
  const colors = {
    'TRUE': 'border-green-300 bg-green-50',
    'FALSE': 'border-red-300 bg-red-50',
    'PARTIALLY TRUE': 'border-yellow-300 bg-yellow-50',
    'UNVERIFIABLE': 'border-gray-300 bg-gray-50'
  }
  return colors[verdict] || 'border-gray-300 bg-gray-50'
}

const getClaimBadgeClass = (verdict) => {
  const classes = {
    'TRUE': 'bg-green-500 text-white',
    'FALSE': 'bg-red-500 text-white',
    'PARTIALLY TRUE': 'bg-yellow-500 text-white',
    'UNVERIFIABLE': 'bg-gray-500 text-white'
  }
  return classes[verdict] || 'bg-gray-500 text-white'
}

const getClaimProgressColor = (verdict) => {
  const colors = {
    'TRUE': 'bg-green-500',
    'FALSE': 'bg-red-500',
    'PARTIALLY TRUE': 'bg-yellow-500',
    'UNVERIFIABLE': 'bg-gray-500'
  }
  return colors[verdict] || 'bg-gray-500'
}

const getReliabilityBadgeClass = (reliability) => {
  const classes = {
    'high': 'bg-green-100 text-green-800',
    'medium': 'bg-yellow-100 text-yellow-800',
    'low': 'bg-red-100 text-red-800'
  }
  return classes[reliability] || 'bg-gray-100 text-gray-800'
}
</script>

<style scoped>
/* Add any component-specific styles here */
</style>

