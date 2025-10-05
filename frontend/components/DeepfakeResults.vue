<template>
  <div class="mt-8 mx-4 bg-white rounded-3xl shadow-2xl overflow-hidden p-6 md:p-8">
    <!-- Alert Header -->
    <div class="text-center mb-8 border-4 border-red-500 rounded-2xl p-6">
      <div class="inline-flex items-center justify-center w-24 h-24 bg-red-100 rounded-full mb-4 animate-pulse">
        <span class="text-5xl">🤖</span>
      </div>
      <h2 class="text-4xl font-bold text-red-600 mb-3">
        AI-Generated Content Detected
      </h2>
      <p class="text-xl text-gray-700 mb-2">{{ deepfakeData.message }}</p>
      <div class="inline-block px-6 py-2 bg-red-100 text-red-800 rounded-full font-semibold text-lg">
        {{ (deepfakeData.probability * 100).toFixed(1) }}% AI-Generated Probability
      </div>
    </div>

    <!-- Main Content Wrapper -->
    <div class="w-full mx-auto flex flex-col gap-6">

    <!-- Warning Message -->
    <div class="bg-red-50 border-l-4 border-red-500 p-6 rounded-xl">
      <div class="flex items-start">
        <span class="text-3xl mr-3">⚠️</span>
        <div>
          <h3 class="font-bold text-red-900 text-lg mb-2">Warning</h3>
          <p class="text-red-800">{{ deepfakeData.warning }}</p>
        </div>
      </div>
    </div>

    <!-- What We Detect -->
    <div class="bg-gradient-to-br from-purple-50 to-blue-50 rounded-2xl p-6 border-2 border-purple-200">
      <h3 class="text-xl font-semibold text-gray-900 mb-4">🔍 What We Detect</h3>
      <p class="text-gray-700 mb-4">Our AI analyzes images for various types of synthetic and manipulated content:</p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div class="bg-white rounded-xl p-4 shadow-sm">
          <div class="flex items-start gap-3">
            <span class="text-2xl">🤖</span>
            <div>
              <h4 class="font-semibold text-gray-900 mb-1">AI-Generated Faces</h4>
              <p class="text-sm text-gray-600">Synthetic faces created by GANs, diffusion models, and other generative AI</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-xl p-4 shadow-sm">
          <div class="flex items-start gap-3">
            <span class="text-2xl">🎭</span>
            <div>
              <h4 class="font-semibold text-gray-900 mb-1">Hyperrealistic Face Swaps</h4>
              <p class="text-sm text-gray-600">Deepfake face replacements and identity manipulations</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-xl p-4 shadow-sm">
          <div class="flex items-start gap-3">
            <span class="text-2xl">✨</span>
            <div>
              <h4 class="font-semibold text-gray-900 mb-1">Digital Artifacts</h4>
              <p class="text-sm text-gray-600">Unnatural patterns, inconsistencies, and generation signatures</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-xl p-4 shadow-sm">
          <div class="flex items-start gap-3">
            <span class="text-2xl">🖼️</span>
            <div>
              <h4 class="font-semibold text-gray-900 mb-1">Synthetic Media</h4>
              <p class="text-sm text-gray-600">AI-generated images, scenes, and manipulated photographs</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Example Comparison -->
      <div class="mt-6">
        <h4 class="font-semibold text-gray-900 mb-3 text-center">📸 Example Comparison</h4>
        <div class="grid grid-cols-2 gap-4">
          <!-- Real Person -->
          <div class="bg-white rounded-xl shadow-md overflow-hidden">
            <img 
              src="/assets/images/real_person.png" 
              alt="Real Person" 
              class="w-full h-auto"
            />
            <div class="p-3 bg-green-50 text-center">
              <span class="inline-block px-3 py-1 bg-green-500 text-white rounded-full text-sm font-bold">
                ✅ REAL
              </span>
              <p class="text-xs text-gray-600 mt-2">Authentic photograph</p>
            </div>
          </div>
          
          <!-- AI Generated -->
          <div class="bg-white rounded-xl shadow-md overflow-hidden">
            <img 
              src="/assets/images/ai_person.png" 
              alt="AI Generated Person" 
              class="w-full h-auto"
            />
            <div class="p-3 bg-red-50 text-center">
              <span class="inline-block px-3 py-1 bg-red-500 text-white rounded-full text-sm font-bold">
                ⚠️ AI GENERATED
              </span>
              <p class="text-xs text-gray-600 mt-2">Synthetic face</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Model Results -->
    <div>
      <h3 class="text-xl font-semibold text-gray-900 mb-4">🔬 Individual Model Results</h3>
      <p class="text-sm text-gray-600 mb-4">Results from {{ deepfakeData.per_model_results.length }} different AI detection models:</p>
      
      <div class="space-y-3">
        <div 
          v-for="(model, index) in deepfakeData.per_model_results" 
          :key="index"
          class="bg-gray-50 rounded-xl p-4 border border-gray-200 hover:border-purple-300 transition-all"
        >
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-3">
              <span class="text-2xl">{{ model.detected_as_fake ? '🚨' : '✅' }}</span>
              <span class="font-semibold text-gray-900">{{ model.model }}</span>
            </div>
            <span 
              class="px-3 py-1 rounded-full text-sm font-bold"
              :class="model.detected_as_fake ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'"
            >
              {{ (model.probability * 100).toFixed(1) }}%
            </span>
          </div>
          <div class="bg-white rounded-lg h-2 overflow-hidden">
            <div 
              class="h-full transition-all duration-500"
              :class="model.detected_as_fake ? 'bg-red-500' : 'bg-green-500'"
              :style="{ width: `${model.probability * 100}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Average Score -->
    <div class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border-2 border-purple-200">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-purple-900 mb-1">📈 Average Detection Score</h3>
          <p class="text-sm text-gray-600">Combined result from all models</p>
        </div>
        <div class="text-right">
          <div class="text-3xl font-bold text-purple-600">
            {{ (deepfakeData.average_probability * 100).toFixed(1) }}%
          </div>
          <div class="text-sm text-gray-600">AI-Generated</div>
        </div>
      </div>
    </div>

    <!-- Info Section -->
    <div class="bg-blue-50 border-l-4 border-blue-500 p-6 rounded-xl">
      <div class="flex items-start">
        <span class="text-2xl mr-3">💡</span>
        <div>
          <h3 class="font-bold text-blue-900 text-lg mb-2">What does this mean?</h3>
          <ul class="text-blue-800 space-y-2 text-sm">
            <li>• This image was likely created or significantly manipulated by AI technology</li>
            <li>• Multiple detection models analyzed different aspects of the image</li>
            <li>• The content may not represent real events, people, or products</li>
            <li>• Exercise caution when sharing or using this image</li>
          </ul>
        </div>
      </div>
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

    </div> <!-- End Main Content Wrapper -->
  </div>
</template>

<script setup>
const props = defineProps({
  deepfakeData: {
    type: Object,
    required: true
  }
})

defineEmits(['reset'])
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

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
