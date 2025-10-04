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
        <div v-if="!isCapturingCriteria" class="bg-white rounded-3xl shadow-2xl overflow-hidden max-w-md mx-auto">
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
              @click="flipCamera"
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

            <!-- Detected Item Overlay -->
            <div v-if="capturedImage && detectedItem" class="absolute top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-10">
              <p class="text-sm font-semibold">✓ Detected:</p>
              <p class="text-lg font-bold">{{ detectedItem }}</p>
            </div>

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

        <!-- Criteria Capture Section -->
        <div v-if="isCapturingCriteria && !analysisResult" class="bg-white rounded-3xl shadow-2xl overflow-hidden max-w-md mx-auto">
          <!-- Camera View -->
          <div class="relative bg-gray-900 flex items-center justify-center" style="aspect-ratio: 3/4; min-height: 500px;">
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
            <div v-if="isCameraActive" class="absolute top-4 left-4 flex items-center gap-2 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-semibold z-10">
              <span class="w-2 h-2 bg-white rounded-full animate-pulse"></span>
              LIVE
            </div>

            <!-- Flip Camera Button -->
            <button 
              v-if="isCameraActive"
              @click="flipCamera"
              class="absolute top-4 right-16 bg-white text-gray-800 p-2 rounded-full shadow-lg hover:bg-gray-100 transition-all z-10"
              title="Flip camera"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>

            <!-- Current Criterion Overlay -->
            <div class="absolute top-4 right-4 bg-purple-600 text-white px-4 py-3 rounded-lg shadow-lg z-10">
              <p class="text-xs font-semibold">Criterion {{ currentCriterionIndex + 1 }} of {{ detectionResult.location_angle.length }}</p>
            </div>

            <!-- Camera Overlay Grid -->
            <div v-if="isCameraActive" class="absolute inset-0 pointer-events-none">
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

          <!-- Instructions and Controls -->
          <div class="p-8 bg-gradient-to-br from-purple-50 to-white">
            <!-- Current Criterion Instructions -->
            <div class="mb-6 p-6 bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl border-l-4 border-purple-500">
              <p class="text-lg font-semibold text-gray-900 mb-2">
                📷 {{ detectionResult.location_angle[currentCriterionIndex] }}
              </p>
              <p class="text-sm text-gray-600">Position your item according to this instruction and capture a clear photo.</p>
            </div>

            <!-- Progress Indicators -->
            <div class="mb-6 flex gap-2 justify-center flex-wrap">
              <div 
                v-for="(_, index) in detectionResult.location_angle" 
                :key="index"
                :class="[
                  'w-12 h-12 rounded-full flex items-center justify-center font-bold transition-all',
                  index < currentCriterionIndex ? 'bg-green-500 text-white' : 
                  index === currentCriterionIndex ? 'bg-purple-600 text-white animate-pulse' : 
                  'bg-gray-200 text-gray-400'
                ]"
              >
                {{ index + 1 }}
              </div>
            </div>

            <!-- Camera Controls for Criteria -->
            <div class="flex gap-4 justify-center flex-wrap">
              <button 
                v-if="isCameraActive"
                @click="captureCriterionPhoto"
                class="px-8 py-4 bg-purple-600 text-white text-lg font-semibold rounded-full hover:bg-purple-700 transition-all duration-300 hover:scale-105 shadow-lg"
              >
                📸 Capture
              </button>
              
              <button 
                v-if="currentCriterionIndex > 0"
                @click="retakeCriterionPhoto"
                class="px-8 py-4 bg-yellow-500 text-white text-lg font-semibold rounded-full hover:bg-yellow-600 transition-all duration-300"
              >
                ↩️ Retake Previous
              </button>

              <button 
                @click="resetCamera"
                class="px-8 py-4 bg-white text-purple-600 border-2 border-purple-600 text-lg font-semibold rounded-full hover:bg-purple-50 transition-all duration-300"
              >
                ✕ Cancel
              </button>
            </div>
          </div>
        </div>

        <!-- Analysis Results Section -->
        <div v-if="analysisResult" class="mt-8 bg-white rounded-3xl shadow-2xl overflow-hidden p-8">
          <h2 class="text-4xl font-bold text-center mb-8">
            <span v-if="analysisResult.is_authentic" class="text-green-600">✓ Authentic</span>
            <span v-else class="text-red-600">✗ Counterfeit</span>
          </h2>

          <!-- Overall Confidence -->
          <div class="mb-6 p-6 bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl text-center">
            <p class="text-sm text-gray-600 mb-2">Overall Confidence</p>
            <p class="text-4xl font-bold text-purple-600">{{ (analysisResult.overall_confidence * 100).toFixed(1) }}%</p>
          </div>

          <!-- Summary -->
          <div class="mb-6 p-6 bg-gray-50 rounded-2xl">
            <h3 class="text-xl font-semibold text-gray-900 mb-3">Summary</h3>
            <p class="text-gray-700">{{ analysisResult.summary }}</p>
          </div>

          <!-- Criteria Results -->
          <div class="mb-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-4">Detailed Results</h3>
            <div class="space-y-3">
              <div 
                v-for="(result, index) in analysisResult.criteria_results" 
                :key="index"
                :class="[
                  'p-4 rounded-xl border-l-4',
                  result.passed ? 'bg-green-50 border-green-500' : 'bg-red-50 border-red-500'
                ]"
              >
                <div class="flex items-start gap-3">
                  <div class="flex-shrink-0">
                    <span v-if="result.passed" class="text-2xl">✓</span>
                    <span v-else class="text-2xl">✗</span>
                  </div>
                  <div class="flex-1">
                    <p class="font-semibold text-gray-900 mb-1">{{ result.criterion }}</p>
                    <p class="text-sm text-gray-600 mb-2">{{ result.notes }}</p>
                    <p class="text-xs text-gray-500">Confidence: {{ (result.confidence * 100).toFixed(1) }}%</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-4 justify-center">
            <button 
              @click="resetCamera"
              class="px-8 py-4 bg-purple-600 text-white text-lg font-semibold rounded-full hover:bg-purple-700 transition-all duration-300 hover:scale-105 shadow-lg"
            >
              🔄 Check Another Item
            </button>
          </div>
        </div>

        <!-- Results Section -->
        <div v-if="showResults && detectionResult && !isCapturingCriteria && !analysisResult" ref="criteriaSection" class="mt-8 bg-white rounded-3xl shadow-2xl overflow-hidden p-8">
          <h2 class="text-3xl font-bold text-gray-900 mb-6">✨ Detection Results</h2>
          
          <!-- Item Info -->
          <div class="mb-6 p-6 bg-purple-50 rounded-2xl">
            <h3 class="text-xl font-semibold text-purple-900 mb-2">Detected Item</h3>
            <p class="text-2xl font-bold text-purple-600">{{ detectionResult.item }}</p>
            <p class="text-sm text-gray-600 mt-2">Detection ID: {{ detectionResult.detection_id }}</p>
          </div>

          <!-- Camera Instructions -->
          <div class="mb-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-4">📸 Next Steps: Capture These Views</h3>
            <p class="text-gray-600 mb-4">Please take photos of the following angles to verify authenticity:</p>
            
            <div class="space-y-4">
              <div 
                v-for="(location, index) in detectionResult.location_angle" 
                :key="index"
                class="p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border-l-4 border-purple-500"
              >
                <div class="flex items-start gap-3">
                  <div class="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold">
                    {{ index + 1 }}
                  </div>
                  <div class="flex-1">
                    <p class="font-semibold text-gray-900">
                      📷 {{ location }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-4 justify-center">
            <button 
              @click="continueToCapture"
              class="px-8 py-4 bg-purple-600 text-white text-lg font-semibold rounded-full hover:bg-purple-700 transition-all duration-300 hover:scale-105 shadow-lg"
            >
              📸 Continue to Capture
            </button>
            <button 
              @click="resetCamera"
              class="px-8 py-4 bg-white text-purple-600 border-2 border-purple-600 text-lg font-semibold rounded-full hover:bg-purple-50 transition-all duration-300"
            >
              🔄 Start Over
            </button>
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
const criteriaSection = ref(null)
const capturedImage = ref(null)
const isCameraActive = ref(false)
const isProcessing = ref(false)
const processingStep = ref('Analyzing...')
const stream = ref(null)
const detectionResult = ref(null)
const detectedItem = ref(null)
const showResults = ref(false)
const isCapturingCriteria = ref(false)
const currentCriterionIndex = ref(0)
const criteriaImages = ref([])
const analysisResult = ref(null)
const facingMode = ref('environment') // 'user' for front, 'environment' for back
const cameraPermissionGranted = ref(false)

const requestCameraPermission = async () => {
  try {
    // Request camera permission
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: true,
      audio: false 
    })
    
    // Stop the stream immediately, we just needed to ask for permission
    stream.getTracks().forEach(track => track.stop())
    
    cameraPermissionGranted.value = true
    return true
  } catch (error) {
    console.error('Camera permission denied:', error)
    alert('Camera permission is required to use this feature. Please allow camera access and try again.')
    return false
  }
}

const startCamera = async () => {
  try {
    // Check if we have permission first
    if (!cameraPermissionGranted.value) {
      const granted = await requestCameraPermission()
      if (!granted) return
    }

    // Request camera with higher quality settings (portrait orientation)
    const constraints = {
      video: {
        facingMode: facingMode.value,
        width: { ideal: 1080 },
        height: { ideal: 1920 }
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

const flipCamera = async () => {
  // Toggle between front and back camera
  facingMode.value = facingMode.value === 'environment' ? 'user' : 'environment'
  
  // Stop current stream
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop())
  }
  
  // Restart camera with new facing mode
  await startCamera()
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
  detectionResult.value = null
  detectedItem.value = null
  showResults.value = false
  isCapturingCriteria.value = false
  currentCriterionIndex.value = 0
  criteriaImages.value = []
  analysisResult.value = null
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
  processingStep.value = 'Detecting item...'
  
  try {
    // Step 1: Detect the item
    const detectResponse = await fetch(`${API_URL}/detect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image: capturedImage.value
      })
    })
    
    if (!detectResponse.ok) {
      throw new Error('Failed to detect item')
    }
    
    const detectResult = await detectResponse.json()
    
    // Handle repositioning case
    if (detectResult.needs_repositioning) {
      alert(`📷 Repositioning Needed\n\n${detectResult.repositioning_instructions}`)
      capturedImage.value = null
      isProcessing.value = false
      startCamera()
      return
    }
    
    // Handle error case
    if (!detectResult.success) {
      alert(`❌ Error: ${detectResult.error || 'Unknown error occurred'}`)
      isProcessing.value = false
      return
    }
    
    console.log('✅ Item detected:', detectResult.item)
    
    // Show detected item on screen immediately
    detectedItem.value = detectResult.item
    isProcessing.value = false
    
    // Wait a moment for user to see the detected item
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // Step 2: Get criteria for the detected item
    isProcessing.value = true
    processingStep.value = 'Getting authentication criteria...'
    
    const criteriaResponse = await fetch(`${API_URL}/criteria/${detectResult.detection_id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    
    if (!criteriaResponse.ok) {
      throw new Error('Failed to get criteria')
    }
    
    const criteriaResult = await criteriaResponse.json()
    
    if (!criteriaResult.success) {
      alert(`❌ Error: ${criteriaResult.error || 'Failed to get criteria'}`)
      isProcessing.value = false
      return
    }
    
    console.log('✅ Criteria fetched:', criteriaResult.location_angle.length, 'items')
    
    // Combine results for display
    detectionResult.value = {
      ...detectResult,
      location_angle: criteriaResult.location_angle
    }
    
    isProcessing.value = false
    showResults.value = true
    
    // Auto-scroll to criteria section
    await nextTick()
    if (criteriaSection.value) {
      criteriaSection.value.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
    
  } catch (error) {
    console.error('Error analyzing image:', error)
    alert(`❌ Error analyzing image. Make sure the backend is running at ${API_URL}`)
    isProcessing.value = false
  }
}

const continueToCapture = () => {
  isCapturingCriteria.value = true
  currentCriterionIndex.value = 0
  criteriaImages.value = []
  capturedImage.value = null
  showResults.value = false
  startCamera()
}

const captureCriterionPhoto = () => {
  if (!videoElement.value || !canvasElement.value) return
  
  const video = videoElement.value
  const canvas = canvasElement.value
  
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  
  const context = canvas.getContext('2d')
  context.drawImage(video, 0, 0, canvas.width, canvas.height)
  
  const imageData = canvas.toDataURL('image/jpeg')
  criteriaImages.value.push(imageData)
  
  // Move to next criterion or finish
  if (currentCriterionIndex.value < detectionResult.value.location_angle.length - 1) {
    currentCriterionIndex.value++
  } else {
    // All criteria captured, stop camera and analyze
    stopCamera()
    submitForAnalysis()
  }
}

const retakeCriterionPhoto = () => {
  if (criteriaImages.value.length > 0) {
    criteriaImages.value.pop()
    if (currentCriterionIndex.value > 0) {
      currentCriterionIndex.value--
    }
  }
}

const submitForAnalysis = async () => {
  isProcessing.value = true
  processingStep.value = 'Analyzing authenticity...'
  
  try {
    const response = await fetch(`${API_URL}/analyze/${detectionResult.value.detection_id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        images: criteriaImages.value
      })
    })
    
    if (!response.ok) {
      throw new Error('Failed to analyze images')
    }
    
    const result = await response.json()
    
    if (!result.success) {
      alert(`❌ Error: ${result.error || 'Analysis failed'}`)
      return
    }
    
    console.log('✅ Analysis complete:', result)
    analysisResult.value = result
    isCapturingCriteria.value = false
    
  } catch (error) {
    console.error('Error analyzing images:', error)
    alert(`❌ Error analyzing images. Make sure the backend is running at ${API_URL}`)
  } finally {
    isProcessing.value = false
  }
}

onMounted(async () => {
  // Request camera permission on page load
  await requestCameraPermission()
})

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

