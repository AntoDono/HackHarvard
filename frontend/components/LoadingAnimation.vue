<template>
  <div class="text-center text-white">
    <div 
      class="text-6xl md:text-8xl font-bold mb-6 transition-all duration-300"
      :class="{ 'animate-shake': isShaking }"
      :style="{ color: getRealColor(currentReal) }"
    >
      {{ currentReal }}real?
    </div>
    <p class="text-xl md:text-2xl font-semibold">{{ message }}</p>
    <p class="text-sm text-gray-300 mt-2">This may take a few moments...</p>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  message: {
    type: String,
    default: 'Processing...'
  }
})

const currentReal = ref(1)
const isShaking = ref(false)
let intervalId = null

const getRealColor = (num) => {
  const colors = {
    1: '#ec4899', // pink-500
    2: '#a855f7', // purple-500
    3: '#8b5cf6', // violet-500
    4: '#6366f1'  // indigo-500
  }
  return colors[num] || '#a855f7'
}

const cycleReals = () => {
  intervalId = setInterval(() => {
    if (currentReal.value === 4) {
      // Trigger shake animation at 4real
      isShaking.value = true
      
      // Remove shake and reset after shake duration
      setTimeout(() => {
        isShaking.value = false
        currentReal.value = 1
      }, 1000)
    } else {
      currentReal.value++
    }
  }, 1000) // Change every 600ms
}

onMounted(() => {
  cycleReals()
})

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId)
  }
})

// Watch for message changes to restart animation
watch(() => props.message, () => {
  currentReal.value = 1
  isShaking.value = false
})
</script>

<style scoped>
@keyframes shake {
  0%, 100% {
    transform: translateX(0) rotate(0deg);
  }
  10%, 30%, 50%, 70%, 90% {
    transform: translateX(-8px) rotate(-2deg);
  }
  20%, 40%, 60%, 80% {
    transform: translateX(8px) rotate(2deg);
  }
}

.animate-shake {
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}
</style>

