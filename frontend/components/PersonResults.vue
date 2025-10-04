<template>
  <div class="mt-8 mx-4 bg-white rounded-3xl shadow-2xl overflow-hidden p-6 md:p-8">
    <h2 class="text-4xl font-bold text-center mb-8">
      <span class="text-purple-600">👤 {{ personName }}</span>
    </h2>

    <!-- Main Content -->
    <div class="w-full mx-auto flex flex-col lg:flex-row gap-6">
        
        <!-- Left Column -->
        <div class="w-full lg:w-1/2 space-y-4">
          <!-- Statistics Grid -->
          <div class="grid grid-cols-2 md:grid-cols-2 gap-4">
            <div class="bg-gray-50 rounded-xl p-4 text-center">
              <p class="text-3xl font-bold text-gray-900">{{ statistics?.total_findings || 0 }}</p>
              <p class="text-sm text-gray-600">Total Findings</p>
            </div>
            <div class="bg-green-50 rounded-xl p-4 text-center">
              <p class="text-3xl font-bold text-green-600">{{ statistics?.positive_findings || 0 }}</p>
              <p class="text-sm text-gray-600">Positive</p>
            </div>
            <div class="bg-red-50 rounded-xl p-4 text-center">
              <p class="text-3xl font-bold text-red-600">{{ statistics?.negative_findings || 0 }}</p>
              <p class="text-sm text-gray-600">Negative</p>
            </div>
            <div class="bg-blue-50 rounded-xl p-4 text-center">
              <p class="text-3xl font-bold text-blue-600">{{ statistics?.date_range || 'N/A' }}</p>
              <p class="text-sm text-gray-600">Time Period</p>
            </div>
          </div>

          <!-- Fakeness Score -->
          <div class="p-6 rounded-2xl text-center" :class="getScoreBackground(fakenessScore)">
            <p class="text-sm text-gray-600 mb-2">Fakeness Score</p>
            <p class="text-5xl font-bold mb-2" :class="getScoreColor(fakenessScore)">
              {{ fakenessScore }}/100
            </p>
            <p class="text-lg font-semibold" :class="getScoreColor(fakenessScore)">
              {{ overallAssessment }}
            </p>
          </div>

          <!-- Summary -->
          <div class="p-6 bg-gray-50 rounded-2xl">
            <h3 class="text-xl font-semibold text-gray-900 mb-3">Executive Summary</h3>
            <p class="text-gray-700 leading-relaxed">{{ summary }}</p>
          </div>

          <!-- Red Flags -->
          <div v-if="redFlags && redFlags.length > 0" class="p-6 bg-red-50 rounded-2xl border-2 border-red-200">
            <h3 class="text-xl font-semibold text-red-900 mb-4 flex items-center gap-2">
              <span>🚩</span> Red Flags
            </h3>
            <ul class="space-y-2">
              <li v-for="(flag, index) in redFlags" :key="index" class="flex items-start gap-2">
                <span class="text-red-600 mt-1">•</span>
                <span class="text-red-900">{{ flag }}</span>
              </li>
            </ul>
          </div>

        </div>

        <!-- Right Column - Findings -->
        <div class="w-full lg:w-1/2 space-y-4">
          <!-- Positive Findings -->
          <div v-if="positiveFindings && positiveFindings.length > 0">
            <h3 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span>🌟</span> Positive Findings
            </h3>
            <div class="space-y-4">
              <div 
                v-for="(finding, index) in positiveFindings" 
                :key="index"
                class="p-5 rounded-xl border-l-4 shadow-sm bg-green-50 border-green-500"
              >
                <div class="mb-3">
                  <div class="flex items-start justify-between gap-4 mb-2">
                    <h4 class="font-bold text-gray-900 text-lg">{{ finding.title }}</h4>
                    <span class="px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap bg-green-200 text-green-900">
                      {{ finding.category }}
                    </span>
                  </div>
                  <div class="flex flex-wrap gap-4 text-sm text-gray-600 mb-2">
                    <span>📅 {{ finding.date }}</span>
                    <span>🏷️ {{ finding.category }}</span>
                  </div>
                </div>
                
                <p class="text-gray-700 mb-3 leading-relaxed">{{ finding.description }}</p>
                
                <div v-if="finding.source" class="border-t pt-3 mt-3">
                  <p class="text-xs uppercase font-semibold text-gray-500 mb-1">Source</p>
                  <a 
                    :href="formatSourceUrl(finding.source)" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    class="inline-flex items-center gap-2 px-3 py-1.5 bg-green-100 hover:bg-green-200 text-green-700 hover:text-green-800 rounded-lg transition-colors text-sm font-medium"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                    <span>View Source</span>
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              </div>
            </div>
          </div>

          <!-- Negative Findings -->
          <div v-if="negativeFindings && negativeFindings.length > 0">
            <h3 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span>⚠️</span> Negative Findings
            </h3>
            <div class="space-y-4">
              <div 
                v-for="(finding, index) in negativeFindings" 
                :key="index"
                class="p-5 rounded-xl border-l-4 shadow-sm"
                :class="getSeverityClass(finding.severity)"
              >
                <div class="mb-3">
                  <div class="flex items-start justify-between gap-4 mb-2">
                    <h4 class="font-bold text-gray-900 text-lg">{{ finding.title }}</h4>
                    <span 
                      class="px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap"
                      :class="getSeverityBadge(finding.severity)"
                    >
                      {{ finding.severity }}
                    </span>
                  </div>
                  <div class="flex flex-wrap gap-4 text-sm text-gray-600 mb-2">
                    <span>📅 {{ finding.date }}</span>
                    <span>🏷️ {{ finding.category }}</span>
                    <span v-if="'verified' in finding">
                      <span v-if="finding.verified" class="text-green-600 font-semibold">✅ Verified</span>
                      <span v-else class="text-orange-600">⚠️ Unverified</span>
                    </span>
                    <span v-if="finding.public_reaction" class="capitalize">
                      👥 {{ finding.public_reaction }} reaction
                    </span>
                  </div>
                </div>
                
                <p class="text-gray-700 mb-3 leading-relaxed">{{ finding.description }}</p>
                
                <div v-if="finding.source" class="border-t pt-3 mt-3">
                  <p class="text-xs uppercase font-semibold text-gray-500 mb-1">Source</p>
                  <a 
                    :href="formatSourceUrl(finding.source)" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    class="inline-flex items-center gap-2 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 hover:text-blue-800 rounded-lg transition-colors text-sm font-medium"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                    <span>View Source</span>
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    
    <!-- Action Button -->
    <div class="flex gap-4 justify-center mt-8">
      <button 
        @click="$emit('reset')"
        class="px-8 py-4 bg-purple-600 text-white text-lg font-semibold rounded-full hover:bg-purple-700 transition-all duration-300 hover:scale-105 shadow-lg"
      >
        🔄 Check Another Person
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  personName: String,
  fakenessScore: Number,
  overallAssessment: String,
  summary: String,
  findings: Array,
  redFlags: Array,
  positiveNotes: Array,
  statistics: Object,
  searchMetadata: Object
})

defineEmits(['reset'])

// Computed properties to filter findings
const positiveFindings = computed(() => {
  if (!props.findings) return []
  return props.findings.filter(f => f.type === 'positive')
})

const negativeFindings = computed(() => {
  if (!props.findings) return []
  return props.findings.filter(f => f.type === 'negative')
})

const formatDate = (timestamp) => {
  if (!timestamp) return 'Just now'
  const date = new Date(timestamp)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
}

const formatSourceUrl = (url) => {
  if (!url) return '#'
  // If the URL doesn't start with http:// or https://, add https://
  if (!url.match(/^https?:\/\//)) {
    return 'https://' + url
  }
  return url
}

const getScoreColor = (score) => {
  if (score <= 30) return 'text-green-600'
  if (score <= 60) return 'text-yellow-600'
  return 'text-red-600'
}

const getScoreBackground = (score) => {
  if (score <= 30) return 'bg-gradient-to-r from-green-50 to-green-100'
  if (score <= 60) return 'bg-gradient-to-r from-yellow-50 to-yellow-100'
  return 'bg-gradient-to-r from-red-50 to-red-100'
}

const getSeverityClass = (severity) => {
  if (!severity) return 'bg-gray-50 border-gray-400'
  const severityLower = severity.toLowerCase()
  if (severityLower === 'high' || severityLower === 'critical') {
    return 'bg-red-50 border-red-400'
  } else if (severityLower === 'medium' || severityLower === 'moderate') {
    return 'bg-yellow-50 border-yellow-400'
  }
  return 'bg-blue-50 border-blue-400'
}

const getSeverityBadge = (severity) => {
  if (!severity) return 'bg-gray-200 text-gray-900'
  const severityLower = severity.toLowerCase()
  if (severityLower === 'high' || severityLower === 'critical') {
    return 'bg-red-200 text-red-900'
  } else if (severityLower === 'medium' || severityLower === 'moderate') {
    return 'bg-yellow-200 text-yellow-900'
  }
  return 'bg-blue-200 text-blue-900'
}
</script>

