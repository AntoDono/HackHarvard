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

        <!-- Features Grid -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mt-24 fade-in-up" style="animation-delay: 0.5s">
          <div class="feature-card" v-for="(feature, index) in features" :key="index" :style="`animation-delay: ${0.6 + index * 0.1}s`">
            <div class="text-4xl mb-3">{{ feature.icon }}</div>
            <div class="text-sm font-semibold text-gray-700">{{ feature.title }}</div>
          </div>
        </div>
      </div>

      <!-- Floating Elements -->
      <div class="floating-element" style="top: 20%; left: 10%;">💎</div>
      <div class="floating-element" style="top: 30%; right: 15%; animation-delay: 1s;">👜</div>
      <div class="floating-element" style="top: 60%; left: 15%; animation-delay: 2s;">🎨</div>
      <div class="floating-element" style="top: 70%; right: 10%; animation-delay: 1.5s;">🤖</div>
    </div>

    <!-- How It Works Section -->
    <div class="py-20 bg-white">
      <div class="max-w-6xl mx-auto px-8">
        <div class="text-center mb-16 fade-in-up" style="animation-delay: 0.6s">
          <h2 class="text-5xl font-bold text-gray-900 mb-4">How It Works</h2>
          <p class="text-xl text-gray-600">Powered by real-time interactive AI with always up-to-date information</p>
        </div>

        <div class="grid md:grid-cols-3 gap-8 mb-16">
          <!-- Step 1 -->
          <div class="text-center p-8 bg-gradient-to-br from-purple-50 to-white rounded-3xl shadow-lg fade-in-up" style="animation-delay: 0.7s">
            <div class="w-16 h-16 bg-purple-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">1</div>
            <h3 class="text-xl font-bold text-gray-900 mb-3">Capture or Upload</h3>
            <p class="text-gray-600">
              Take a photo or upload images of the item, person, or content you want to verify. Our system works with anything.
            </p>
          </div>

          <!-- Step 2 -->
          <div class="text-center p-8 bg-gradient-to-br from-purple-50 to-white rounded-3xl shadow-lg fade-in-up" style="animation-delay: 0.8s">
            <div class="w-16 h-16 bg-purple-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">2</div>
            <h3 class="text-xl font-bold text-gray-900 mb-3">Real-Time AI Analysis</h3>
            <p class="text-gray-600">
              Our AI searches the web in real-time for the latest authentication criteria, then uses vision models to analyze your image.
            </p>
          </div>

          <!-- Step 3 -->
          <div class="text-center p-8 bg-gradient-to-br from-purple-50 to-white rounded-3xl shadow-lg fade-in-up" style="animation-delay: 0.9s">
            <div class="w-16 h-16 bg-purple-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">3</div>
            <h3 class="text-xl font-bold text-gray-900 mb-3">Get Instant Results</h3>
            <p class="text-gray-600">
              Receive detailed authenticity reports with confidence scores, visual evidence, and expert-level explanations.
            </p>
          </div>
        </div>

        <!-- Technology Stack -->
        <div class="bg-gradient-to-br from-purple-600 to-purple-700 rounded-3xl p-10 text-white fade-in-up" style="animation-delay: 1s">
          <h3 class="text-3xl font-bold mb-8 text-center">Powered by Cutting-Edge AI</h3>
          
          <div class="grid md:grid-cols-2 gap-8">
            <div>
              <h4 class="text-xl font-semibold mb-3 flex items-center gap-2">
                <span class="text-2xl">🌐</span> Real-Time Web Intelligence
              </h4>
              <p class="text-purple-100">
                Our system searches the internet live for the most up-to-date authentication criteria. No outdated databases—just fresh, accurate information every time.
              </p>
            </div>

            <div>
              <h4 class="text-xl font-semibold mb-3 flex items-center gap-2">
                <span class="text-2xl">👁️</span> Multi-Modal Vision AI
              </h4>
              <p class="text-purple-100">
                Advanced CLIP and Gemini models analyze images against specific criteria—checking colors, patterns, materials, stitching, and more.
              </p>
            </div>

            <div>
              <h4 class="text-xl font-semibold mb-3 flex items-center gap-2">
                <span class="text-2xl">📊</span> Confidence Scoring
              </h4>
              <p class="text-purple-100">
                Get objective similarity scores powered by neural networks. Every result includes confidence levels so you know exactly how certain we are.
              </p>
            </div>

            <div>
              <h4 class="text-xl font-semibold mb-3 flex items-center gap-2">
                <span class="text-2xl">⚡</span> Smart Caching
              </h4>
              <p class="text-purple-100">
                Using embedding similarity, we cache results intelligently. Get lightning-fast responses for similar items while staying current.
              </p>
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
</style>