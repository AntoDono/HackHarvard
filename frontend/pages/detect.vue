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

        <!-- Detected Item Badge (Outside Canvas) -->
        <div v-if="capturedImage && detectedItem && !isCapturingCriteria" class="mb-4 mx-auto max-w-md">
          <div class="bg-green-500 text-white px-6 py-3 rounded-2xl shadow-lg text-center">
            <p class="text-sm font-semibold">✓ Detected:</p>
            <p class="text-xl font-bold">{{ detectedItem }}</p>
          </div>
        </div>

        <!-- Camera Section for Initial Detection -->
        <CameraView
          v-if="!isCapturingCriteria && !showResults && !analysisResult"
          ref="cameraViewRef"
          :captured-image="capturedImage"
          :is-camera-active="isCameraActive"
          :is-processing="isProcessing"
          :processing-step="processingStep"
          @start-camera="startCamera"
          @stop-camera="stopCamera"
          @capture="capturePhoto"
          @retake="retakePhoto"
          @analyze="analyzeImage"
          @flip-camera="flipCamera"
          @file-upload="handleFileUpload"
        />

        <!-- Criteria Capture Section -->
        <CriteriaCapture
          v-if="isCapturingCriteria && !analysisResult"
          ref="criteriaCaptureRef"
          :current-index="currentCriterionIndex"
          :total-steps="detectionResult?.location_angle?.length || 0"
          :current-instruction="detectionResult?.location_angle?.[currentCriterionIndex] || ''"
          :is-camera-active="isCameraActive"
          :is-processing="isProcessing"
          :processing-step="processingStep"
          @capture="captureCriterionPhoto"
          @retake-previous="retakeCriterionPhoto"
          @cancel="resetCamera"
          @flip-camera="flipCamera"
        />

        <!-- Canvas for capturing (hidden, shared between both camera modes) -->
        <canvas ref="canvasElement" class="hidden"></canvas>

        <!-- Analysis Results Section -->
        <AnalysisResults
          v-if="analysisResult"
          :result="analysisResult"
          @reset="resetCamera"
        />

        <!-- Detection Results Section -->
        <DetectionResults
          v-if="showResults && detectionResult && !isCapturingCriteria && !analysisResult"
          ref="criteriaSection"
          :item="detectionResult.item"
          :detection-id="detectionResult.detection_id"
          :location-angles="detectionResult.location_angle"
          @continue="continueToCapture"
          @reset="resetCamera"
        />

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

const config = useRuntimeConfig()
const API_URL = config.public.apiUrl

const cameraViewRef = ref(null)
const criteriaCaptureRef = ref(null)
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
    
    // Get the appropriate video element from the active component
    const activeVideoElement = isCapturingCriteria.value 
      ? criteriaCaptureRef.value?.videoElement 
      : cameraViewRef.value?.videoElement
    
    // Now attach stream to video element
    if (activeVideoElement) {
      activeVideoElement.srcObject = stream.value
      
      // Ensure video plays
      activeVideoElement.onloadedmetadata = () => {
        activeVideoElement.play()
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
  const video = cameraViewRef.value?.videoElement
  const canvas = canvasElement.value
  
  if (!video || !canvas) return
  
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
      criteriaSection.value.$el.scrollIntoView({ behavior: 'smooth', block: 'start' })
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
  const video = criteriaCaptureRef.value?.videoElement
  const canvas = canvasElement.value
  
  if (!video || !canvas) {
    console.error('Video or canvas element not found', { 
      video: video, 
      canvas: canvas 
    })
    alert('Camera not ready. Please try again.')
    return
  }
  
  // Check if video is actually playing
  if (video.readyState < 2) {
    console.error('Video not ready')
    alert('Video not ready. Please wait a moment and try again.')
    return
  }
  
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  
  const context = canvas.getContext('2d')
  context.drawImage(video, 0, 0, canvas.width, canvas.height)
  
  const imageData = canvas.toDataURL('image/jpeg')
  criteriaImages.value.push(imageData)
  
  console.log(`Captured criterion ${currentCriterionIndex.value + 1}`, { 
    totalImages: criteriaImages.value.length 
  })
  
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

