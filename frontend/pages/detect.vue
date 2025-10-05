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

        <!-- Camera Section for Initial Detection -->
        <CameraView
          v-if="!isCapturingCriteria && !showResults && !analysisResult && !showPersonInput && !personResearchResult && !factCheckResult && !deepfakeResult"
          ref="cameraViewRef"
          :captured-image="capturedImage"
          :is-camera-active="isCameraActive"
          :is-processing="isProcessing"
          :processing-step="processingStep"
          :facing-mode="facingMode"
          :zoom-level="zoomLevel"
          :min-zoom="minZoom"
          :max-zoom="maxZoom"
          @start-camera="startCamera"
          @stop-camera="stopCamera"
          @capture="capturePhoto"
          @retake="retakePhoto"
          @analyze="analyzeImage"
          @flip-camera="flipCamera"
          @file-upload="handleFileUpload"
          @zoom-in="zoomIn"
          @zoom-out="zoomOut"
          @reset-zoom="resetZoom"
        />

        <!-- Criteria Capture Section -->
        <CriteriaCapture
          v-if="isCapturingCriteria && !analysisResult"
          ref="criteriaCaptureRef"
          :current-index="currentCriterionIndex"
          :total-steps="detectionResult?.location_angle?.length || 0"
          :current-instruction="detectionResult?.location_angle?.[currentCriterionIndex] || ''"
          :current-detailed-criterion="detectionResult?.detailed_criteria?.[currentCriterionIndex]"
          :is-camera-active="isCameraActive"
          :is-processing="isProcessing"
          :processing-step="processingStep"
          :facing-mode="facingMode"
          :zoom-level="zoomLevel"
          :min-zoom="minZoom"
          :max-zoom="maxZoom"
          @capture="captureCriterionPhoto"
          @retake-previous="retakeCriterionPhoto"
          @cancel="resetCamera"
          @flip-camera="flipCamera"
          @zoom-in="zoomIn"
          @zoom-out="zoomOut"
          @reset-zoom="resetZoom"
        />

        <!-- Canvas for capturing (hidden, shared between both camera modes) -->
        <canvas ref="canvasElement" class="hidden"></canvas>

        <!-- Analysis Results Section (Product) -->
        <AnalysisResults
          v-if="analysisResult"
          :result="analysisResult"
          :criteria-images="criteriaImages"
          :product-name="detectionResult?.item"
          :product-image="detectionResult?.product_image"
          :product-url="detectionResult?.product_url"
          @reset="resetCamera"
        />

        <!-- Person Input Section -->
        <PersonInput
          v-if="showPersonInput"
          :detection-id="detectionResult?.detection_id"
          :image-src="capturedImage"
          :description="detectionResult?.description"
          :confidence="detectionResult?.confidence"
          @research="handlePersonResearch"
          @reset="resetCamera"
        />

        <!-- Deepfake Detection Results Section -->
        <DeepfakeResults
          v-if="deepfakeResult"
          :deepfake-data="deepfakeResult"
          @reset="resetCamera"
        />

        <!-- Person Research Results Section -->
        <PersonResults
          v-if="personResearchResult"
          :person-name="personResearchResult.person_name"
          :fakeness-score="personResearchResult.fakeness_score"
          :overall-assessment="personResearchResult.overall_assessment"
          :summary="personResearchResult.summary"
          :findings="personResearchResult.findings"
          :red-flags="personResearchResult.red_flags"
          :positive-notes="personResearchResult.positive_notes"
          :statistics="personResearchResult.statistics"
          :search-metadata="personResearchResult.search_metadata"
          @reset="resetCamera"
        />

        <!-- Fact Check Results Section (Text) -->
        <FactCheckResults
          v-if="factCheckResult"
          :image-type="factCheckResult.image_type"
          :contains-factual-claims="factCheckResult.contains_factual_claims"
          :overall-verdict="factCheckResult.overall_verdict"
          :confidence-score="factCheckResult.confidence_score"
          :claims="factCheckResult.claims"
          :summary="factCheckResult.summary"
          :important-notes="factCheckResult.important_notes"
          @reset="resetCamera"
        />

        <!-- Detection Results Section (Product) -->
        <DetectionResults
          v-if="showResults && detectionResult && !isCapturingCriteria && !analysisResult"
          ref="criteriaSection"
          :item="detectionResult.item"
          :detection-id="detectionResult.detection_id"
          :location-angles="detectionResult.location_angle"
          :product-image="detectionResult.product_image"
          :product-url="detectionResult.product_url"
          :price-range="detectionResult.price_range"
          @continue="continueToCapture"
          @reset="resetCamera"
        />

      </div>
    </div>

    <!-- Processing Overlay (for criteria fetching) -->
    <div 
      v-if="isProcessing && !isCameraActive && !showDetectionModal" 
      class="loading-overlay"
    >
      <div class="w-full h-full flex items-center justify-center p-4">
        <LoadingAnimation :message="processingStep" />
      </div>
    </div>

    <!-- Detection Modal Popup -->
    <div 
      v-if="showDetectionModal && detectionResult" 
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm p-4"
      @click.self="closeDetectionModal"
    >
      <div class="bg-white rounded-3xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto transform transition-all animate-modal-in">
        <!-- Modal Header -->
        <div class="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6 rounded-t-3xl">
          <div class="flex items-center justify-between">
            <h2 class="text-3xl font-bold">✨ Item Detected!</h2>
            <button 
              @click="closeDetectionModal" 
              class="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2 transition-all"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Modal Content -->
        <div class="p-8">
          <!-- Product Info Card -->
          <div class="mb-6 p-6 bg-gradient-to-br from-purple-50 via-pink-50 to-purple-50 rounded-2xl border-2 border-purple-200">
            <div class="flex flex-col md:flex-row gap-6 items-center">
              <!-- Product Image -->
              <div v-if="detectionResult.product_image" class="flex-shrink-0">
                <img 
                  :src="detectionResult.product_image" 
                  :alt="detectionResult.item"
                  class="w-40 h-40 object-cover rounded-xl shadow-lg border-4 border-white"
                />
              </div>
              
              <!-- Product Info -->
              <div class="flex-1 text-center md:text-left">
                <h3 class="text-xl font-semibold text-purple-900 mb-2">Detected Item</h3>
                <p class="text-3xl font-bold text-purple-600 mb-4">{{ detectionResult.item }}</p>
                
                <!-- Price Range -->
                <div v-if="detectionResult.price_range && (detectionResult.price_range[0] > 0 || detectionResult.price_range[1] > 0)" class="mb-4">
                  <p class="text-xl font-semibold text-gray-700">
                    💰 Price Range: 
                    <span class="text-green-600">
                      ${{ detectionResult.price_range[0].toFixed(2) }} - ${{ detectionResult.price_range[1].toFixed(2) }}
                    </span>
                  </p>
                </div>
                
                <a 
                  v-if="detectionResult.product_url" 
                  :href="detectionResult.product_url" 
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-flex items-center gap-2 px-5 py-3 bg-purple-600 text-white font-semibold rounded-full hover:bg-purple-700 transition-all shadow-md hover:shadow-lg"
                >
                  <span>🌐 View Product Page</span>
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            </div>
            <p class="text-xs text-gray-500 mt-4 text-center border-t border-purple-200 pt-3">Detection ID: {{ detectionResult.detection_id }}</p>
          </div>

          <!-- Brand Input -->
          <div class="mb-6 p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl border-2 border-blue-200">
            <h3 class="text-lg font-semibold text-blue-900 mb-3">🏷️ Specify Brand (Optional)</h3>
            <p class="text-sm text-gray-600 mb-4">Enter the brand name for more accurate authentication criteria</p>
            <input 
              v-model="userSpecifiedBrand"
              type="text" 
              placeholder="e.g., Louis Vuitton, Gucci, Nike..."
              class="w-full px-4 py-3 border-2 border-blue-300 rounded-xl focus:outline-none focus:border-blue-500 text-lg"
            />
          </div>

          <!-- Next Steps Preview -->
          <div class="mb-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-3">📸 Next Steps</h3>
            <p class="text-gray-600 mb-4">Click "Proceed to Verify" to get the verification criteria for this item, or try again if this is not the correct item.</p>
            
            <div class="bg-gradient-to-r from-purple-100 to-pink-100 rounded-xl p-4 border-l-4 border-purple-600">
              <p class="font-semibold text-purple-900 mb-2">🔍 What happens next:</p>
              <p class="text-gray-800">We'll fetch the authentication criteria and guide you through capturing specific angles and features to verify if this item is authentic.</p>
            </div>
          </div>

          <!-- Confirmation Buttons -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center pt-4">
            <button 
              @click="confirmAndProceed"
              class="flex-1 sm:flex-none px-8 py-4 bg-purple-600 text-white text-lg font-semibold rounded-full hover:bg-purple-700 transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-xl"
            >
              ✓ Proceed to Verify
            </button>
            <button 
              @click="tryAgain"
              class="flex-1 sm:flex-none px-8 py-4 bg-white text-purple-600 border-2 border-purple-600 text-lg font-semibold rounded-full hover:bg-purple-50 transition-all duration-300"
            >
              🔄 Try Again
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import LoadingAnimation from '~/components/LoadingAnimation.vue'

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
const showDetectionModal = ref(false)
const isCapturingCriteria = ref(false)
const currentCriterionIndex = ref(0)
const criteriaImages = ref([])
const analysisResult = ref(null)
const facingMode = ref('environment') // 'user' for front, 'environment' for back
const cameraPermissionGranted = ref(false)
const showPersonInput = ref(false)
const personResearchResult = ref(null)
const factCheckResult = ref(null)
const zoomLevel = ref(1)
const minZoom = ref(1)
const maxZoom = ref(3)
const userSpecifiedBrand = ref('')
const deepfakeResult = ref(null)

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

const applyZoom = async (level) => {
  if (!stream.value) return
  
  const track = stream.value.getVideoTracks()[0]
  const capabilities = track.getCapabilities()
  
  if (capabilities.zoom) {
    minZoom.value = capabilities.zoom.min
    maxZoom.value = capabilities.zoom.max
    
    // Clamp zoom level to valid range
    const clampedZoom = Math.max(minZoom.value, Math.min(maxZoom.value, level))
    zoomLevel.value = clampedZoom
    
    await track.applyConstraints({
      advanced: [{ zoom: clampedZoom }]
    })
  }
}

const zoomIn = async () => {
  const newZoom = Math.min(maxZoom.value, zoomLevel.value + 0.5)
  await applyZoom(newZoom)
}

const zoomOut = async () => {
  const newZoom = Math.max(minZoom.value, zoomLevel.value - 0.5)
  await applyZoom(newZoom)
}

const resetZoom = async () => {
  await applyZoom(1)
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
    
    // Get zoom capabilities
    const track = stream.value.getVideoTracks()[0]
    const capabilities = track.getCapabilities()
    
    if (capabilities.zoom) {
      minZoom.value = capabilities.zoom.min
      maxZoom.value = capabilities.zoom.max
      zoomLevel.value = capabilities.zoom.min || 1
    }
    
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
  showDetectionModal.value = false
  isCapturingCriteria.value = false
  currentCriterionIndex.value = 0
  criteriaImages.value = []
  analysisResult.value = null
  showPersonInput.value = false
  personResearchResult.value = null
  factCheckResult.value = null
  deepfakeResult.value = null
  userSpecifiedBrand.value = ''
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
  processingStep.value = 'Detecting...'
  
  // Prevent scrolling when processing
  document.body.style.overflow = 'hidden'
  
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
    
    console.log('✅ Detection result:', detectResult)
    
    // Check for deepfake detection first
    if (detectResult.is_deepfake && detectResult.deepfake_detection) {
      console.log('🤖 DEEPFAKE DETECTED:', detectResult.deepfake_detection.probability)
      deepfakeResult.value = detectResult.deepfake_detection
      isProcessing.value = false
      document.body.style.overflow = 'auto'
      return
    }
    
    // Store detection result
    detectionResult.value = detectResult
    detectedItem.value = detectResult.item || detectResult.person_name
    
    isProcessing.value = false
    
    document.body.style.overflow = 'auto'
    
    // Handle different item types
    if (detectResult.item_type === 'person' && detectResult.awaiting_person_input) {
      // Person detected - show input form
      console.log('👤 Person detected - showing input form')
      showPersonInput.value = true
    } else if (detectResult.item_type === 'text' && detectResult.fact_check) {
      // Text/document detected - show fact check results
      console.log('📄 Text detected - showing fact check results')
      factCheckResult.value = detectResult.fact_check
    } else {
      // Product detected - show modal popup
      showDetectionModal.value = true
    }
    
  } catch (error) {
    console.error('Error analyzing image:', error)
    alert(`❌ Error analyzing image. Make sure the backend is running at ${API_URL}`)
    isProcessing.value = false
    
    document.body.style.overflow = 'auto'
  }
}

const closeDetectionModal = () => {
  showDetectionModal.value = false
}

const confirmAndProceed = async () => {
  showDetectionModal.value = false
  isProcessing.value = true
  processingStep.value = 'Getting authentication criteria...'
  
  document.body.style.overflow = 'hidden'
  
  try {
    // Fetch criteria for the detected item (with optional brand)
    const requestBody = userSpecifiedBrand.value ? { brand: userSpecifiedBrand.value } : {}
    
    const criteriaResponse = await fetch(`${API_URL}/criteria/${detectionResult.value.detection_id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
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
    
    // Add criteria to detection result (both simple and detailed)
    detectionResult.value = {
      ...detectionResult.value,
      location_angle: criteriaResult.location_angle,
      detailed_criteria: criteriaResult.detailed_criteria || []
    }
    
    isProcessing.value = false
    showResults.value = true
    
    document.body.style.overflow = 'auto'
    
    // Auto-scroll to criteria section
    await nextTick()
    if (criteriaSection.value) {
      criteriaSection.value.$el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
    
  } catch (error) {
    console.error('Error getting criteria:', error)
    alert(`❌ Error getting criteria. Make sure the backend is running at ${API_URL}`)
    isProcessing.value = false
    
    document.body.style.overflow = 'auto'
  }
}

const tryAgain = () => {
  // Close modal and reset to try detection again
  showDetectionModal.value = false
  capturedImage.value = null
  detectionResult.value = null
  detectedItem.value = null
  showResults.value = false
  startCamera()
}

const handlePersonResearch = async (data) => {
  isProcessing.value = true
  processingStep.value = 'Researching person...'
  
  document.body.style.overflow = 'hidden'
  
  try {
    const response = await fetch(`${API_URL}/research_person`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    })
    
    if (!response.ok) {
      throw new Error('Failed to research person')
    }
    
    const result = await response.json()
    
    if (!result.success) {
      alert(`❌ Error: ${result.error || 'Failed to research person'}`)
      isProcessing.value = false
      return
    }
    
    console.log('✅ Person research complete:', result)
    
    // Store and display research results
    personResearchResult.value = result.person_research
    showPersonInput.value = false
    isProcessing.value = false
    
    document.body.style.overflow = 'auto'
    
  } catch (error) {
    console.error('Error researching person:', error)
    alert(`❌ Error researching person. Make sure the backend is running at ${API_URL}`)
    isProcessing.value = false
    
    // Re-enable scrolling on error
    document.body.style.overflow = 'auto'
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
  
  // Prevent scrolling when processing
  document.body.style.overflow = 'hidden'
  
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
    
    // Re-enable scrolling
    document.body.style.overflow = 'auto'
    
  } catch (error) {
    console.error('Error analyzing images:', error)
    alert(`❌ Error analyzing images. Make sure the backend is running at ${API_URL}`)
  } finally {
    isProcessing.value = false
    
    // Re-enable scrolling
    document.body.style.overflow = 'auto'
  }
}

onMounted(async () => {
  // Request camera permission on page load
  await requestCameraPermission()
})

onUnmounted(() => {
  stopCamera()
  
  // Ensure scrolling is re-enabled when component unmounts
  document.body.style.overflow = 'auto'
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

@keyframes modal-in {
  0% {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.animate-modal-in {
  animation: modal-in 0.3s ease-out forwards;
}

/* Loading Overlay - Covers Everything */
.loading-overlay {
  position: fixed;
  top: -10vh;
  left: -10vw;
  right: -10vw;
  bottom: -10vh;
  width: 120vw;
  height: 120vh;
  min-height: 120vh;
  min-width: 120vw;
  z-index: 9999;
  background-color: rgba(0, 0, 0, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* Mobile-specific loading overlay fixes */
@media (max-width: 768px) {
  .loading-overlay {
    position: fixed !important;
    top: -20vh !important;
    left: -20vw !important;
    right: -20vw !important;
    bottom: -20vh !important;
    width: 140vw !important;
    height: 140vh !important;
    min-height: 140vh !important;
    min-width: 140vw !important;
    z-index: 9999 !important;
    background: rgba(0, 0, 0, 1) !important;
  }
}

/* Prevent body scroll when loading */
body.loading-overlay-active {
  overflow: hidden !important;
  position: fixed !important;
  width: 100% !important;
  height: 100% !important;
}
</style>

