<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 to-white">
    <!-- Navigation -->
    <nav class="px-8 py-6 flex justify-between items-center border-b border-purple-100">
      <NuxtLink to="/" class="text-3xl font-bold text-purple-600 hover:text-purple-700 transition-colors">
        4real?
      </NuxtLink>
      <button @click="resetCamera" class="px-4 py-2 text-purple-600 hover:bg-purple-50 rounded-full transition-all">
        Reset
      </button>
    </nav>

    <!-- Main Content -->
    <div class="container mx-auto px-8 py-12">
      <div class="max-w-4xl mx-auto">
        <!-- Header -->
        <div class="text-center mb-12">
          <h1 class="text-5xl font-bold text-gray-900 mb-4">Detect Authenticity</h1>
          <p class="text-xl text-gray-600 mb-2">Take a photo to verify if it's real or fake</p>
          <p class="text-md text-purple-600 font-semibold">Powered by real-time AI with always up-to-date information</p>
        </div>

        <!-- Camera Section -->
        <div class="bg-white rounded-3xl shadow-2xl overflow-hidden">
          <!-- Camera View or Preview -->
          <div class="relative aspect-video bg-gray-900 flex items-center justify-center">
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
                <p class="text-xl font-semibold">Analyzing...</p>
              </div>
            </div>
          </div>

          <!-- Canvas for capturing (hidden) -->
          <canvas ref="canvasElement" class="hidden"></canvas>

          <!-- Controls -->
          <div class="p-8 bg-gradient-to-br from-purple-50 to-white">
            <div v-if="!capturedImage" class="flex flex-col sm:flex-row gap-4 justify-center">
              <button 
                v-if="!isCameraActive"
                @click="startCamera"
                class="px-8 py-4 bg-purple-600 text-white text-lg font-semibold rounded-full hover:bg-purple-700 transition-all duration-300 hover:scale-105 shadow-lg"
              >
                📷 Start Camera
              </button>
              
              <button 
                v-if="isCameraActive"
                @click="capturePhoto"
                class="px-8 py-4 bg-purple-600 text-white text-lg font-semibold rounded-full hover:bg-purple-700 transition-all duration-300 hover:scale-105 shadow-lg animate-pulse"
              >
                📸 Capture Photo
              </button>

              <button 
                v-if="isCameraActive"
                @click="stopCamera"
                class="px-8 py-4 bg-white text-purple-600 border-2 border-purple-600 text-lg font-semibold rounded-full hover:bg-purple-50 transition-all duration-300"
              >
                Stop Camera
              </button>
            </div>

            <div v-if="capturedImage" class="flex flex-col sm:flex-row gap-4 justify-center">
              <button 
                @click="analyzeImage"
                :disabled="isProcessing"
                class="px-8 py-4 bg-purple-600 text-white text-lg font-semibold rounded-full hover:bg-purple-700 transition-all duration-300 hover:scale-105 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                🔍 Analyze Image
              </button>
              
              <button 
                @click="retakePhoto"
                class="px-8 py-4 bg-white text-purple-600 border-2 border-purple-600 text-lg font-semibold rounded-full hover:bg-purple-50 transition-all duration-300"
              >
                🔄 Retake
              </button>
            </div>

            <!-- Upload Option -->
            <div class="mt-6 text-center">
              <label class="cursor-pointer inline-flex items-center gap-2 text-purple-600 hover:text-purple-700 font-semibold">
                <span>📁 Or upload an image</span>
                <input 
                  type="file" 
                  accept="image/*" 
                  @change="handleFileUpload"
                  class="hidden"
                />
              </label>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

const config = useRuntimeConfig()
const API_URL = config.public.apiUrl

const videoElement = ref(null)
const canvasElement = ref(null)
const capturedImage = ref(null)
const isCameraActive = ref(false)
const isProcessing = ref(false)
const stream = ref(null)

const startCamera = async () => {
  try {
    // Request camera with higher quality settings
    const constraints = {
      video: {
        facingMode: 'environment',
        width: { ideal: 1920 },
        height: { ideal: 1080 }
      },
      audio: false
    }
    
    stream.value = await navigator.mediaDevices.getUserMedia(constraints)
    
    // Set camera active first to show video element
    isCameraActive.value = true
    
    // Wait for DOM to update
    await nextTick()
    
    // Now attach stream to video element
    if (videoElement.value) {
      videoElement.value.srcObject = stream.value
      
      // Ensure video plays
      videoElement.value.onloadedmetadata = () => {
        videoElement.value.play()
      }
    }
  } catch (error) {
    console.error('Error accessing camera:', error)
    isCameraActive.value = false
    alert('Unable to access camera. Please make sure you have granted camera permissions.')
  }
}

const stopCamera = () => {
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop())
    stream.value = null
    isCameraActive.value = false
  }
}

const capturePhoto = () => {
  if (!videoElement.value || !canvasElement.value) return
  
  const video = videoElement.value
  const canvas = canvasElement.value
  
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  
  const context = canvas.getContext('2d')
  context.drawImage(video, 0, 0, canvas.width, canvas.height)
  
  capturedImage.value = canvas.toDataURL('image/jpeg')
  stopCamera()
}

const retakePhoto = () => {
  capturedImage.value = null
  startCamera()
}

const resetCamera = () => {
  capturedImage.value = null
  stopCamera()
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      capturedImage.value = e.target.result
      stopCamera()
    }
    reader.readAsDataURL(file)
  }
}

const analyzeImage = async () => {
  if (!capturedImage.value) return
  
  isProcessing.value = true
  
  try {
    // Call backend API
    const response = await fetch(`${API_URL}/detect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image: capturedImage.value
      })
    })
    
    if (!response.ok) {
      throw new Error('Failed to analyze image')
    }
    
    const result = await response.json()
    
    // Show results
    alert(`✅ Analysis Complete!\n\nAuthentic: ${result.is_authentic ? 'Yes' : 'No'}\nConfidence: ${(result.confidence * 100).toFixed(1)}%\nItem: ${result.detected_item}\n\nImage saved: ${result.filename}`)
    
  } catch (error) {
    console.error('Error analyzing image:', error)
    alert(`❌ Error analyzing image. Make sure the backend is running at ${API_URL}`)
  } finally {
    isProcessing.value = false
  }
}

onUnmounted(() => {
  stopCamera()
})
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
</style>

