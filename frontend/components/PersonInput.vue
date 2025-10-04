<template>
  <div class="mt-8 mx-4 bg-white rounded-3xl shadow-2xl overflow-hidden p-6 md:p-8">
    <h2 class="text-3xl font-bold text-gray-900 mb-6">👤 Person Detected</h2>
    
    <div class="max-w-4xl mx-auto">
        <!-- Person Image and Details Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Person Image -->
          <div class="flex justify-center">
            <img 
              :src="imageSrc" 
              alt="Detected person"
              class="w-full max-w-sm rounded-xl shadow-lg border-2 border-purple-200"
            />
          </div>

          <!-- Details and Form -->
          <div class="space-y-4">
            <!-- Description -->
            <div class="p-4 bg-purple-50 rounded-xl">
              <p class="text-gray-700 mb-2">
                <span class="font-semibold">AI Detection:</span> {{ description }}
              </p>
              <p class="text-sm text-gray-600">
                <span class="font-semibold">Confidence:</span> {{ confidence }}
              </p>
            </div>

            <!-- Input Form -->
            <div class="space-y-4">
              <div>
                <label for="personName" class="block text-sm font-semibold text-gray-700 mb-2">
                  Person's Name <span class="text-red-500">*</span>
                </label>
                <input 
                  id="personName"
                  v-model="personName"
                  type="text" 
                  placeholder="e.g., John Doe"
                  class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all"
                  required
                />
              </div>

              <div>
                <label for="additionalInfo" class="block text-sm font-semibold text-gray-700 mb-2">
                  Additional Information <span class="text-gray-400">(optional)</span>
                </label>
                <input 
                  id="additionalInfo"
                  v-model="additionalInfo"
                  type="text" 
                  placeholder="e.g., CEO of XYZ Corp, Actor, etc."
                  class="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all"
                />
                <p class="text-xs text-gray-500 mt-1">This helps us find more relevant information</p>
              </div>

              <!-- Action Buttons -->
              <div class="flex gap-4 mt-6">
                <button 
                  @click="submitResearch"
                  :disabled="!personName.trim() || isResearching"
                  class="flex-1 px-6 py-3 bg-purple-600 text-white font-semibold rounded-full hover:bg-purple-700 transition-all duration-300 hover:scale-105 shadow-lg disabled:bg-gray-400 disabled:cursor-not-allowed disabled:hover:scale-100"
                >
                  <span v-if="!isResearching">🔍 Research Person</span>
                  <span v-else>Researching...</span>
                </button>
                <button 
                  @click="$emit('reset')"
                  :disabled="isResearching"
                  class="flex-1 px-6 py-3 bg-white text-purple-600 border-2 border-purple-600 font-semibold rounded-full hover:bg-purple-50 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  🔄 Start Over
                </button>
              </div>
            </div>
          </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  detectionId: String,
  imageSrc: String,
  description: String,
  confidence: String
})

const emit = defineEmits(['research', 'reset'])

const personName = ref('')
const additionalInfo = ref('')
const isResearching = ref(false)

const submitResearch = async () => {
  if (!personName.value.trim()) return
  
  isResearching.value = true
  emit('research', {
    detection_id: props.detectionId,
    person_name: personName.value.trim(),
    additional_info: additionalInfo.value.trim()
  })
}
</script>

