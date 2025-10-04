<template>
  <div class="w-full flex justify-center px-4">
    <div class="bg-white rounded-3xl shadow-2xl overflow-hidden w-full max-w-2xl">
      <!-- Camera View or Preview -->
      <div class="relative bg-gray-900 flex items-center justify-center" style="aspect-ratio: 3/4; max-height: 75vh; width: 100%;">
        <!-- Video Stream (when camera is active) -->
        <video 
          v-if="!capturedImage && isCameraActive" 
          ref="videoElement" 
          autoplay 
          playsinline
          muted
          class="w-full h-full object-contain"
        ></video>

        <!-- Camera Status Indicator -->
        <div v-if="isCameraActive && !capturedImage" class="absolute top-4 left-4 flex items-center gap-2 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-semibold">
          <span class="w-2 h-2 bg-white rounded-full animate-pulse"></span>
          LIVE
        </div>

        <!-- Camera Control Buttons -->
        <div v-if="isCameraActive && !capturedImage" class="absolute top-4 right-4 flex flex-col gap-2 z-10">
          <!-- Flip Camera Button -->
          <button 
            @click="$emit('flip-camera')"
            class="bg-white text-gray-800 p-3 rounded-full shadow-lg hover:bg-gray-100 transition-all"
            title="Flip camera"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          
          <!-- Zoom Controls -->
          <div v-if="maxZoom > minZoom" class="flex flex-col gap-1 bg-white rounded-full shadow-lg p-2">
            <!-- Zoom In -->
            <button 
              @click="$emit('zoom-in')"
              :disabled="zoomLevel >= maxZoom"
              class="p-2 rounded-full hover:bg-gray-100 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              title="Zoom in"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
              </svg>
            </button>
            
            <!-- Zoom Level Indicator -->
            <div class="text-center px-1">
              <span class="text-xs font-bold text-gray-700">{{ zoomLevel.toFixed(1) }}x</span>
            </div>
            
            <!-- Zoom Out -->
            <button 
              @click="$emit('zoom-out')"
              :disabled="zoomLevel <= minZoom"
              class="p-2 rounded-full hover:bg-gray-100 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              title="Zoom out"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Captured Image Preview -->
        <img 
          v-if="capturedImage" 
          :src="capturedImage" 
          alt="Captured" 
          class="w-full h-full object-contain"
        />

        <!-- Placeholder when camera is not active -->
        <div v-if="!capturedImage && !isCameraActive" class="text-center text-white px-4">
          <div class="text-5xl md:text-6xl mb-4">📸</div>
          <p class="text-sm md:text-xl">Click "Start Camera" to begin</p>
        </div>

        <!-- Camera Overlay Grid -->
        <div v-if="isCameraActive && !capturedImage" class="absolute inset-0 pointer-events-none">
          <div class="w-full h-full border-2 border-purple-500 opacity-30"></div>
          <div class="absolute top-1/2 left-0 right-0 h-0.5 bg-purple-500 opacity-20"></div>
          <div class="absolute left-1/2 top-0 bottom-0 w-0.5 bg-purple-500 opacity-20"></div>
        </div>

        <!-- Loading Overlay -->
        <div v-if="isProcessing" class="absolute inset-0 bg-black bg-opacity-80 flex items-center justify-center">
          <LoadingAnimation :message="processingStep" />
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
import LoadingAnimation from './LoadingAnimation.vue'

const videoElement = ref(null)

defineProps({
  capturedImage: String,
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

defineEmits(['start-camera', 'stop-camera', 'capture', 'retake', 'analyze', 'flip-camera', 'file-upload', 'zoom-in', 'zoom-out', 'reset-zoom'])

defineExpose({
  videoElement
})
</script>

