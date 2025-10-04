<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 to-white overflow-hidden">
    <!-- Navigation -->
    <nav class="absolute top-0 left-0 right-0 z-50 px-8 py-6 flex justify-between items-center">
      <div class="text-3xl font-bold text-purple-600 logo-animate">4real?</div>
      <NuxtLink to="/detect" class="px-6 py-2 bg-purple-600 text-white rounded-full hover:bg-purple-700 transition-all duration-300 hover:scale-105">
        Try Now
      </NuxtLink>
    </nav>

    <!-- Hero Section -->
    <div class="container mx-auto px-8 pt-32 pb-20">
      <div class="text-center max-w-5xl mx-auto">
        <!-- Animated Badge -->
        <div class="inline-block mb-8 fade-in-up" style="animation-delay: 0.1s">
          <span class="px-4 py-2 bg-purple-100 text-purple-600 rounded-full text-sm font-semibold">
            🔍 AI-Powered Authentication
          </span>
        </div>

        <!-- Main Headline -->
        <h1 class="text-7xl md:text-8xl font-extrabold text-gray-900 mb-6 fade-in-up" style="animation-delay: 0.2s">
          Is It
          <span class="text-purple-600 inline-block wave-text">4real?</span>
        </h1>

        <!-- Punchline -->
        <p class="text-2xl md:text-3xl text-gray-600 mb-6 fade-in-up max-w-3xl mx-auto" style="animation-delay: 0.3s">
          Because in a world full of fakes, authenticity is everything.
        </p>
        <p class="text-lg md:text-xl text-gray-500 mb-12 fade-in-up max-w-2xl mx-auto" style="animation-delay: 0.35s">
          Real-time AI. Real information. Real confidence.
        </p>

        <!-- CTA Buttons -->
        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center fade-in-up" style="animation-delay: 0.4s">
          <NuxtLink to="/detect" class="px-8 py-4 bg-purple-600 text-white text-lg font-semibold rounded-full hover:bg-purple-700 transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-xl">
            Start Detecting
          </NuxtLink>
          <button class="px-8 py-4 bg-white text-purple-600 text-lg font-semibold rounded-full border-2 border-purple-600 hover:bg-purple-50 transition-all duration-300 hover:scale-105">
            Learn More
          </button>
        </div>

        <!-- Animated Features Marquee -->
        <div class="mt-24">
          <div class="w-screen relative left-1/2 right-1/2 -mx-[50vw] overflow-hidden">
            <div class="marquee-container">
              <div class="marquee-content">
                <div v-for="(feature, index) in features" :key="`first-${index}`" class="feature-badge">
                  <div class="text-3xl">{{ feature.icon }}</div>
                  <div class="text-sm font-semibold text-gray-700">{{ feature.title }}</div>
                </div>
              </div>
              <div class="marquee-content" aria-hidden="true">
                <div v-for="(feature, index) in features" :key="`second-${index}`" class="feature-badge">
                  <div class="text-3xl">{{ feature.icon }}</div>
                  <div class="text-sm font-semibold text-gray-700">{{ feature.title }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Floating Elements -->
      <div class="floating-element" style="top: 20%; left: 10%;">💎</div>
      <div class="floating-element" style="top: 30%; right: 15%; animation-delay: 1s;">👜</div>
      <div class="floating-element" style="top: 60%; left: 15%; animation-delay: 2s;">🎨</div>
      <div class="floating-element" style="top: 70%; right: 10%; animation-delay: 1.5s;">🤖</div>
    </div>

    <!-- See It In Action Section -->
    <div class="py-20 bg-gradient-to-br from-gray-50 to-white">
      <div class="max-w-7xl mx-auto px-8">
        <div class="text-center mb-20 fade-in-up">
          <h2 class="text-5xl font-bold text-gray-900 mb-4">See It In Action</h2>
          <p class="text-xl text-gray-600">Watch how 4real? protects you from counterfeits in real-time</p>
        </div>

        <!-- Feature 1: Snap & Detect (Left Image, Right Text) -->
        <div class="flex flex-col md:flex-row items-center gap-12 mb-24">
          <div class="md:w-1/2 fade-in-left">
            <div class="bg-white rounded-3xl shadow-2xl overflow-hidden transform hover:scale-[1.02] transition-all duration-300">
              <img 
                src="/assets/images/redsox_detect_mobile.png" 
                alt="Snap and Detect" 
                class="w-full h-auto"
              />
            </div>
          </div>
          <div class="md:w-1/2 fade-in-right">
            <div class="inline-block px-4 py-2 bg-purple-100 text-purple-600 rounded-full text-sm font-bold mb-4">
              📸 STEP 1
            </div>
            <h3 class="text-4xl font-bold text-gray-900 mb-6">Snap & Detect</h3>
            <p class="text-xl text-gray-700 mb-6">
              Simply capture a photo or upload an image. Our AI instantly identifies what you're looking at—whether it's a luxury handbag, collectible, electronics, or any product.
            </p>
            <div class="space-y-3">
              <div class="flex items-start gap-3">
                <span class="text-2xl">🤖</span>
                <p class="text-gray-600"><strong>AI Vision Detection:</strong> Recognizes products, brands, and categories automatically</p>
              </div>
              <div class="flex items-start gap-3">
                <span class="text-2xl">🌐</span>
                <p class="text-gray-600"><strong>Reverse Image Search:</strong> Finds authentic reference images from trusted sources</p>
              </div>
              <div class="flex items-start gap-3">
                <span class="text-2xl">💰</span>
                <p class="text-gray-600"><strong>Price Intelligence:</strong> Fetches real-time market prices to verify value</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Feature 2: Guided Capture (Right Image, Left Text) -->
        <div class="flex flex-col md:flex-row-reverse items-center gap-12 mb-24">
          <div class="md:w-1/2 fade-in-right">
            <div class="bg-white rounded-3xl shadow-2xl overflow-hidden transform hover:scale-[1.02] transition-all duration-300">
              <div class="relative">
                <img 
                  src="/assets/images/authentic_jelly_cat.png" 
                  alt="Guided Authentication" 
                  class="w-full h-auto"
                />
              </div>
            </div>
          </div>
          <div class="md:w-1/2 fade-in-left">
            <div class="inline-block px-4 py-2 bg-blue-100 text-blue-600 rounded-full text-sm font-bold mb-4">
              🎯 STEP 2
            </div>
            <h3 class="text-4xl font-bold text-gray-900 mb-6">Guided Photo Capture</h3>
            <p class="text-xl text-gray-700 mb-6">
              Our AI generates specific authentication criteria and guides you through capturing the exact angles and features needed to verify authenticity.
            </p>
            <div class="space-y-3">
              <div class="flex items-start gap-3">
                <span class="text-2xl">🔍</span>
                <p class="text-gray-600"><strong>Smart Criteria:</strong> AI searches the web for the latest authentication markers</p>
              </div>
              <div class="flex items-start gap-3">
                <span class="text-2xl">📍</span>
                <p class="text-gray-600"><strong>On-Screen Guidance:</strong> Shows exactly where to look and what to photograph</p>
              </div>
              <div class="flex items-start gap-3">
                <span class="text-2xl">⚡</span>
                <p class="text-gray-600"><strong>Step-by-Step:</strong> Captures multiple angles for comprehensive analysis</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Feature 3: Authentic Results (Left Image, Right Text) -->
        <div class="flex flex-col md:flex-row items-center gap-12 mb-24">
          <div class="md:w-1/2 fade-in-left">
            <div class="bg-white rounded-3xl shadow-2xl overflow-hidden transform hover:scale-[1.02] transition-all duration-300">
              <img 
                src="/assets/images/authentic_jelly_cat_details.png" 
                alt="Detailed Analysis" 
                class="w-full h-auto"
              />
            </div>
          </div>
          <div class="md:w-1/2 fade-in-right">
            <div class="inline-block px-4 py-2 bg-green-100 text-green-600 rounded-full text-sm font-bold mb-4">
              ✓ AUTHENTIC
            </div>
            <h3 class="text-4xl font-bold text-gray-900 mb-6">Get Instant Results</h3>
            <p class="text-xl text-gray-700 mb-6">
              Receive a comprehensive authenticity report with detailed scoring for each criterion. Our multi-modal AI analyzes colors, patterns, materials, stitching, and more.
            </p>
            <div class="space-y-3">
              <div class="flex items-start gap-3">
                <span class="text-2xl">📊</span>
                <p class="text-gray-600"><strong>Confidence Scores:</strong> See individual criterion scores and overall authenticity rating</p>
              </div>
              <div class="flex items-start gap-3">
                <span class="text-2xl">👁️</span>
                <p class="text-gray-600"><strong>Visual Evidence:</strong> Compare your images side-by-side with analysis notes</p>
              </div>
              <div class="flex items-start gap-3">
                <span class="text-2xl">🧠</span>
                <p class="text-gray-600"><strong>AI Reasoning:</strong> Understand exactly why the verdict was reached</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Feature 4: Counterfeit Detection (Right Image, Left Text) -->
        <div class="flex flex-col md:flex-row-reverse items-center gap-12">
          <div class="md:w-1/2 fade-in-right">
            <div class="bg-white rounded-3xl shadow-2xl overflow-hidden transform hover:scale-[1.02] transition-all duration-300">
              <img 
                src="/assets/images/counterfeit_waterbottle_details.png" 
                alt="Counterfeit Detection" 
                class="w-full h-auto"
              />
            </div>
          </div>
          <div class="md:w-1/2 fade-in-left">
            <div class="inline-block px-4 py-2 bg-red-100 text-red-600 rounded-full text-sm font-bold mb-4">
              ✗ COUNTERFEIT DETECTED
            </div>
            <h3 class="text-4xl font-bold text-gray-900 mb-6">Spot the Fakes</h3>
            <p class="text-xl text-gray-700 mb-6">
              When counterfeits are detected, you'll see exactly what's wrong—failed criteria, low confidence scores, and detailed explanations of the inconsistencies.
            </p>
            <div class="space-y-3">
              <div class="flex items-start gap-3">
                <span class="text-2xl">🚩</span>
                <p class="text-gray-600"><strong>Red Flags:</strong> Highlights specific authentication failures</p>
              </div>
              <div class="flex items-start gap-3">
                <span class="text-2xl">⚠️</span>
                <p class="text-gray-600"><strong>Risk Assessment:</strong> Shows counterfeit probability and confidence levels</p>
              </div>
              <div class="flex items-start gap-3">
                <span class="text-2xl">🛡️</span>
                <p class="text-gray-600"><strong>Protection:</strong> Saves you from purchasing fake items</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- What We Detect Section -->
    <div class="py-20 bg-gradient-to-br from-purple-50 to-white">
      <div class="max-w-6xl mx-auto px-8">
        <div class="text-center mb-16 fade-in-up" style="animation-delay: 0.6s">
          <h2 class="text-5xl font-bold text-gray-900 mb-4">What Can We Detect?</h2>
          <p class="text-xl text-gray-600">From physical items to digital content—if it can be faked, we can verify it</p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div class="bg-white p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
            <div class="text-4xl mb-3">👜</div>
            <h3 class="text-lg font-bold text-gray-900 mb-2">Luxury Brands</h3>
            <p class="text-gray-600 text-sm">Louis Vuitton, Gucci, Chanel, Rolex, and more. We check stitching, logos, materials, and hardware.</p>
          </div>

          <div class="bg-white p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
            <div class="text-4xl mb-3">🎨</div>
            <h3 class="text-lg font-bold text-gray-900 mb-2">AI-Generated Content</h3>
            <p class="text-gray-600 text-sm">Detect AI images, deepfakes, synthetic media. We analyze artifacts, inconsistencies, and telltale signs.</p>
          </div>

          <div class="bg-white p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
            <div class="text-4xl mb-3">👤</div>
            <h3 class="text-lg font-bold text-gray-900 mb-2">People Check</h3>
            <p class="text-gray-600 text-sm">Search for online drama, controversies, crime records. Know who you're dealing with before you trust them.</p>
          </div>

          <div class="bg-white p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
            <div class="text-4xl mb-3">🍔</div>
            <h3 class="text-lg font-bold text-gray-900 mb-2">Food & Beverages</h3>
            <p class="text-gray-600 text-sm">Verify authentic food products, premium ingredients, genuine packaging. No more fake premium goods.</p>
          </div>

          <div class="bg-white p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
            <div class="text-4xl mb-3">🧸</div>
            <h3 class="text-lg font-bold text-gray-900 mb-2">Collectibles</h3>
            <p class="text-gray-600 text-sm">Labubu, sneakers, trading cards, limited editions. Authenticate your collection with confidence.</p>
          </div>

          <div class="bg-white p-6 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
            <div class="text-4xl mb-3">📱</div>
            <h3 class="text-lg font-bold text-gray-900 mb-2">Electronics</h3>
            <p class="text-gray-600 text-sm">iPhones, AirPods, Samsung devices. Check serial numbers, build quality, and authentic components.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom CTA Section -->
    <div class="text-center py-20 bg-white">
      <div class="max-w-3xl mx-auto px-8 fade-in-up" style="animation-delay: 0.8s">
        <h2 class="text-5xl font-bold text-gray-900 mb-6">Don't Get Fooled.</h2>
        <p class="text-2xl text-gray-600 mb-4">
          In a world where counterfeits cost billions and AI deepfakes fool millions...
        </p>
        <p class="text-xl text-purple-600 font-semibold mb-8">
          You deserve to know what's 4real.
        </p>
        <NuxtLink to="/detect" class="inline-block px-12 py-5 bg-purple-600 text-white text-xl font-bold rounded-full hover:bg-purple-700 transition-all duration-300 hover:scale-105 shadow-2xl">
          Try 4real? Now — It's Free
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup>
const features = [
  { icon: '👜', title: 'Luxury Brands' },
  { icon: '🍔', title: 'Food & Drinks' },
  { icon: '🎨', title: 'AI Content' },
  { icon: '👤', title: 'People Check' },
  { icon: '🧸', title: 'Collectibles' },
  { icon: '📱', title: 'Electronics' },
  { icon: '💊', title: 'Health Products' },
  { icon: '🔍', title: 'And More...' }
]
</script>

<style scoped>
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes fadeInRight {
  from {
    opacity: 0;
    transform: translateX(50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes scroll {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-100%);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(5deg);
  }
}

@keyframes wave {
  0%, 100% {
    transform: rotate(-3deg);
  }
  50% {
    transform: rotate(3deg);
  }
}

@keyframes logoFloat {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.fade-in-up {
  animation: fadeInUp 0.8s ease-out forwards;
  opacity: 0;
}

.fade-in-left {
  animation: fadeInLeft 1s ease-out forwards;
  opacity: 0;
}

.fade-in-right {
  animation: fadeInRight 1s ease-out forwards;
  opacity: 0;
}

.floating-element {
  position: absolute;
  font-size: 3rem;
  opacity: 0.1;
  animation: float 3s ease-in-out infinite;
  pointer-events: none;
}

.wave-text {
  animation: wave 2s ease-in-out infinite;
  transform-origin: center;
}

.logo-animate {
  animation: logoFloat 2s ease-in-out infinite;
}

/* Marquee Styles */
.marquee-container {
  display: flex;
  overflow: hidden;
  user-select: none;
  gap: 2rem;
  padding: 1rem 0;
}

.marquee-content {
  flex-shrink: 0;
  display: flex;
  justify-content: space-around;
  gap: 3rem;
  min-width: 100%;
  animation: scroll 30s linear infinite;
  padding: 0 2rem;
}

.feature-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem 2rem;
  background: white;
  border-radius: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  min-width: 150px;
  white-space: nowrap;
}

.feature-badge:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(147, 51, 234, 0.15);
}

.feature-card {
  padding: 2rem;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  animation: fadeInUp 0.8s ease-out forwards;
  opacity: 0;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(147, 51, 234, 0.15);
}

/* Pause marquee on hover */
.marquee-container:hover .marquee-content {
  animation-play-state: paused;
}
</style>