<template>
  <div class="w-full flex justify-center px-4">
    <div class="bg-white rounded-3xl shadow-2xl overflow-hidden w-full max-w-md">
      <!-- Current Criterion Instructions - Above Camera -->
      <div class="p-3 bg-gradient-to-r from-purple-50 to-pink-50 border-b-2 border-purple-200">
        <p class="text-xs font-semibold text-purple-900 text-center mb-1">
          Step {{ currentIndex + 1 }} of {{ totalSteps }}
        </p>
        <p class="text-sm font-semibold text-gray-900 text-center">
          📷 {{ currentInstruction }}
        </p>
      </div>

      <!-- Camera View -->
      <div class="relative bg-gray-900 flex items-center justify-center mx-auto" style="aspect-ratio: 3/4; max-height: 60vh; width: 100%;">
        <!-- Video Stream -->
        <video 
          v-if="isCameraActive" 
          ref="videoElement" 
          autoplay 
          playsinline
          muted
          class="w-full h-full object-contain"
        ></video>

        <!-- Camera Status Indicator -->
        <div v-if="isCameraActive" class="absolute top-2 left-2 flex items-center gap-1 bg-red-500 text-white px-2 py-1 rounded-full text-xs font-semibold z-10">
          <span class="w-1.5 h-1.5 bg-white rounded-full animate-pulse"></span>
          LIVE
        </div>

        <!-- Flip Camera Button -->
        <button 
          v-if="isCameraActive"
          @click="$emit('flip-camera')"
          class="absolute top-2 right-2 bg-white text-gray-800 p-2 rounded-full shadow-lg hover:bg-gray-100 transition-all z-10"
          title="Flip camera"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>

        <!-- Camera Overlay Grid -->
        <div v-if="isCameraActive" class="absolute inset-0 pointer-events-none">
          <div class="w-full h-full border-2 border-purple-500 opacity-30"></div>
          <div class="absolute top-1/2 left-0 right-0 h-0.5 bg-purple-500 opacity-20"></div>
          <div class="absolute left-1/2 top-0 bottom-0 w-0.5 bg-purple-500 opacity-20"></div>
        </div>

        <!-- Loading Overlay -->
        <div v-if="isProcessing" class="absolute inset-0 bg-black bg-opacity-70 flex items-center justify-center">
          <div class="text-center text-white">
            <div class="animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent mx-auto mb-3"></div>
            <p class="text-lg font-semibold">{{ processingStep }}</p>
          </div>
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

const videoElement = ref(null)

defineProps({
  currentIndex: Number,
  totalSteps: Number,
  currentInstruction: String,
  isCameraActive: Boolean,
  isProcessing: Boolean,
  processingStep: String
})

defineEmits(['capture', 'retake-previous', 'cancel', 'flip-camera'])

defineExpose({
  videoElement
})
</script>

