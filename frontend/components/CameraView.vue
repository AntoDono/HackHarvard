<template>
  <div class="w-full flex justify-center px-4">
    <div class="bg-white rounded-3xl shadow-2xl overflow-hidden w-full max-w-md">
      <!-- Camera View or Preview -->
      <div class="relative bg-gray-900 flex items-center justify-center" style="aspect-ratio: 3/4; min-height: 500px;">
        <!-- Video Stream (when camera is active) -->
        <video 
          v-if="!capturedImage && isCameraActive" 
          ref="videoElement" 
          autoplay 
          playsinline
          muted
          class="w-full h-full object-cover"
        ></video>

        <!-- Camera Status Indicator -->
        <div v-if="isCameraActive && !capturedImage" class="absolute top-4 left-4 flex items-center gap-2 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-semibold">
          <span class="w-2 h-2 bg-white rounded-full animate-pulse"></span>
          LIVE
        </div>

        <!-- Flip Camera Button -->
        <button 
          v-if="isCameraActive && !capturedImage"
          @click="$emit('flip-camera')"
          class="absolute top-4 right-4 bg-white text-gray-800 p-3 rounded-full shadow-lg hover:bg-gray-100 transition-all z-10"
          title="Flip camera"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>

        <!-- Captured Image Preview -->
        <img 
          v-if="capturedImage" 
          :src="capturedImage" 
          alt="Captured" 
          class="w-full h-full object-cover"
        />

        <!-- Placeholder when camera is not active -->
        <div v-if="!capturedImage && !isCameraActive" class="text-center text-white">
          <div class="text-6xl mb-4">📸</div>
          <p class="text-xl">Click "Start Camera" to begin</p>
        </div>

        <!-- Camera Overlay Grid -->
        <div v-if="isCameraActive && !capturedImage" class="absolute inset-0 pointer-events-none">
          <div class="w-full h-full border-2 border-purple-500 opacity-30"></div>
          <div class="absolute top-1/2 left-0 right-0 h-0.5 bg-purple-500 opacity-20"></div>
          <div class="absolute left-1/2 top-0 bottom-0 w-0.5 bg-purple-500 opacity-20"></div>
        </div>

        <!-- Loading Overlay -->
        <div v-if="isProcessing" class="absolute inset-0 bg-black bg-opacity-70 flex items-center justify-center">
          <div class="text-center text-white">
            <div class="animate-spin rounded-full h-16 w-16 border-4 border-purple-500 border-t-transparent mx-auto mb-4"></div>
            <p class="text-xl font-semibold">{{ processingStep }}</p>
          </div>
        </div>
      </div>

      <!-- Controls -->
      <div class="p-6 md:p-8 bg-gradient-to-br from-purple-50 to-white">
        <div v-if="!capturedImage" class="flex flex-col gap-3 justify-center">
          <button 
            v-if="!isCameraActive"
            @click="$emit('start-camera')"
            class="w-full px-6 py-3 bg-purple-600 text-white text-base md:text-lg font-semibold rounded-full hover:bg-purple-700 transition-all duration-300 hover:scale-105 shadow-lg"
          >
            📷 Start Camera
          </button>
          
          <button 
            v-if="isCameraActive"
            @click="$emit('capture')"
            class="w-full px-6 py-3 bg-purple-600 text-white text-base md:text-lg font-semibold rounded-full hover:bg-purple-700 transition-all duration-300 hover:scale-105 shadow-lg animate-pulse"
          >
            📸 Capture Photo
          </button>

          <button 
            v-if="isCameraActive"
            @click="$emit('stop-camera')"
            class="w-full px-6 py-3 bg-white text-purple-600 border-2 border-purple-600 text-base md:text-lg font-semibold rounded-full hover:bg-purple-50 transition-all duration-300"
          >
            Stop Camera
          </button>
        </div>

        <div v-if="capturedImage" class="flex flex-col gap-3 justify-center">
          <button 
            @click="$emit('analyze')"
            :disabled="isProcessing"
            class="w-full px-6 py-3 bg-purple-600 text-white text-base md:text-lg font-semibold rounded-full hover:bg-purple-700 transition-all duration-300 hover:scale-105 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            🔍 Analyze Image
          </button>
          
          <button 
            @click="$emit('retake')"
            class="w-full px-6 py-3 bg-white text-purple-600 border-2 border-purple-600 text-base md:text-lg font-semibold rounded-full hover:bg-purple-50 transition-all duration-300"
          >
            🔄 Retake
          </button>
        </div>

        <!-- Upload Option -->
        <div class="mt-4 text-center">
          <label class="cursor-pointer inline-flex items-center gap-2 text-purple-600 hover:text-purple-700 font-semibold text-sm md:text-base">
            <span>📁 Or upload an image</span>
            <input 
              type="file" 
              accept="image/*" 
              @change="$emit('file-upload', $event)"
              class="hidden"
            />
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const videoElement = ref(null)

defineProps({
  capturedImage: String,
  isCameraActive: Boolean,
  isProcessing: Boolean,
  processingStep: String
})

defineEmits(['start-camera', 'stop-camera', 'capture', 'retake', 'analyze', 'flip-camera', 'file-upload'])

defineExpose({
  videoElement
})
</script>

