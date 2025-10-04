<template>
  <div class="w-full flex justify-center px-4">
    <div class="bg-white rounded-3xl shadow-2xl overflow-hidden w-full max-w-2xl">
      <!-- Current Criterion Instructions - Above Camera -->
      <div class="p-4 bg-gradient-to-r from-purple-50 to-pink-50 border-b-2 border-purple-200">
        <p class="text-xs font-semibold text-purple-900 text-center mb-2">
          Step {{ currentIndex + 1 }} of {{ totalSteps }}
        </p>
        
        <!-- Detailed Criteria if available -->
        <div v-if="currentDetailedCriterion" class="space-y-2 text-left max-w-xl mx-auto">
          <div class="bg-white rounded-lg p-2 shadow-sm">
            <p class="text-xs font-semibold text-purple-700 mb-1">🎯 What to Look For:</p>
            <p class="text-xs text-gray-800">{{ currentDetailedCriterion.primary_feature }}</p>
          </div>
          
          <div class="bg-white rounded-lg p-2 shadow-sm">
            <p class="text-xs font-semibold text-blue-700 mb-1">📍 Where:</p>
            <p class="text-xs text-gray-800">{{ currentDetailedCriterion.primary_location }}</p>
          </div>
          
          <div class="bg-white rounded-lg p-2 shadow-sm">
            <p class="text-xs font-semibold text-green-700 mb-1">📸 How to Photograph:</p>
            <p class="text-xs text-gray-800">{{ currentDetailedCriterion.how_to_photograph }}</p>
          </div>
          
          <div v-if="showBackup" class="bg-yellow-50 rounded-lg p-2 border border-yellow-300">
            <p class="text-xs font-semibold text-yellow-800 mb-1">⚠️ Backup Option:</p>
            <p class="text-xs text-gray-700">{{ currentDetailedCriterion.backup_feature }} - {{ currentDetailedCriterion.backup_location }}</p>
          </div>
        </div>
        
        <!-- Fallback to simple instruction -->
        <p v-else class="text-sm font-semibold text-gray-900 text-center">
          📷 {{ currentInstruction }}
        </p>
      </div>

      <!-- Camera View -->
      <div class="relative bg-gray-900 flex items-center justify-center mx-auto" style="aspect-ratio: 3/4; max-height: 75vh; width: 100%;">
        <!-- Video Stream -->
        <video 
          v-if="isCameraActive" 
          ref="videoElement" 
          autoplay 
          playsinline
          muted
          class="w-full h-full object-cover"
        ></video>

        <!-- Camera Status Indicator -->
        <div v-if="isCameraActive" class="absolute top-2 left-2 flex items-center gap-1 bg-red-500 text-white px-2 py-1 rounded-full text-xs font-semibold z-10">
          <span class="w-1.5 h-1.5 bg-white rounded-full animate-pulse"></span>
          LIVE
        </div>

        <!-- Camera Control Buttons -->
        <div v-if="isCameraActive" class="absolute top-2 right-2 flex flex-col gap-1 z-10">
          <!-- Flip Camera Button -->
          <button 
            @click="$emit('flip-camera')"
            class="bg-white text-gray-800 p-2 rounded-full shadow-lg hover:bg-gray-100 transition-all"
            title="Flip camera"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          
          <!-- Zoom Controls -->
          <div v-if="maxZoom > minZoom" class="flex flex-col gap-1 bg-white rounded-full shadow-lg p-1">
            <!-- Zoom In -->
            <button 
              @click="$emit('zoom-in')"
              :disabled="zoomLevel >= maxZoom"
              class="p-1.5 rounded-full hover:bg-gray-100 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              title="Zoom in"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
              </svg>
            </button>
            
            <!-- Zoom Level Indicator -->
            <div class="text-center px-0.5">
              <span class="text-xs font-bold text-gray-700">{{ zoomLevel.toFixed(1) }}x</span>
            </div>
            
            <!-- Zoom Out -->
            <button 
              @click="$emit('zoom-out')"
              :disabled="zoomLevel <= minZoom"
              class="p-1.5 rounded-full hover:bg-gray-100 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              title="Zoom out"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Camera Overlay Grid -->
        <div v-if="isCameraActive" class="absolute inset-0 pointer-events-none">
          <div class="w-full h-full border-2 border-purple-500 opacity-30"></div>
          <div class="absolute top-1/2 left-0 right-0 h-0.5 bg-purple-500 opacity-20"></div>
          <div class="absolute left-1/2 top-0 bottom-0 w-0.5 bg-purple-500 opacity-20"></div>
        </div>

        <!-- Loading Overlay -->
        <div v-if="isProcessing" class="absolute inset-0 bg-black bg-opacity-80 flex items-center justify-center">
          <LoadingAnimation :message="processingStep" />
        </div>
      </div>

      <!-- Compact Controls Below Camera -->
      <div class="p-3 bg-gradient-to-br from-purple-50 to-white">
        <!-- Progress Indicators -->
        <div class="mb-3 flex gap-1.5 justify-center">
          <div 
            v-for="index in totalSteps" 
            :key="index"
            :class="[
              'w-8 h-8 rounded-full flex items-center justify-center font-bold transition-all text-xs',
              index - 1 < currentIndex ? 'bg-green-500 text-white' : 
              index - 1 === currentIndex ? 'bg-purple-600 text-white animate-pulse' : 
              'bg-gray-200 text-gray-400'
            ]"
          >
            {{ index }}
          </div>
        </div>

        <!-- Show Backup Button if detailed criteria available -->
        <div v-if="currentDetailedCriterion && currentDetailedCriterion.backup_feature" class="mb-2 text-center">
          <button 
            @click="showBackup = !showBackup"
            class="text-xs px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full hover:bg-yellow-200 transition-all font-medium"
          >
            {{ showBackup ? '✓ Hide' : '⚠️ Show' }} Backup Option
          </button>
        </div>

        <!-- Camera Controls for Criteria -->
        <div class="flex gap-2">
          <button 
            v-if="isCameraActive"
            @click="$emit('capture')"
            class="flex-1 px-4 py-2.5 bg-purple-600 text-white text-sm font-semibold rounded-full hover:bg-purple-700 transition-all shadow-lg"
          >
            📸 Capture
          </button>
          
          <button 
            v-if="currentIndex > 0"
            @click="$emit('retake-previous')"
            class="px-4 py-2.5 bg-yellow-500 text-white text-sm font-semibold rounded-full hover:bg-yellow-600 transition-all"
          >
            ↩️
          </button>

          <button 
            @click="$emit('cancel')"
            class="px-4 py-2.5 bg-white text-purple-600 border-2 border-purple-600 text-sm font-semibold rounded-full hover:bg-purple-50 transition-all"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import LoadingAnimation from './LoadingAnimation.vue'

const videoElement = ref(null)
const showBackup = ref(false)

defineProps({
  currentIndex: Number,
  totalSteps: Number,
  currentInstruction: String,
  currentDetailedCriterion: Object,
  isCameraActive: Boolean,
  isProcessing: Boolean,
  processingStep: String,
  zoomLevel: {
    type: Number,
    default: 1
  },
  minZoom: {
    type: Number,
    default: 1
  },
  maxZoom: {
    type: Number,
    default: 3
  }
})

defineEmits(['capture', 'retake-previous', 'cancel', 'flip-camera', 'zoom-in', 'zoom-out', 'reset-zoom'])

defineExpose({
  videoElement
})
</script>

