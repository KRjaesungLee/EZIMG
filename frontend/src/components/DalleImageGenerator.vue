<template>
  <div class="dalle-container">
    <SectionBox withHeader>
      <template #header>
        <h2>{{ $t('keyword_tags') }}</h2>
        <p>{{ $t('click_to_add') }}</p>
      </template>
      
      <div class="input-section">
        <div class="input-wrapper">
          <label for="prompt-input" class="input-label">{{ $t('prompt_input') }}</label>
          <textarea
            id="prompt-input"
            v-model="prompt"
            :placeholder="$t('prompt_input') + '...'"
            class="prompt-input"
            rows="4"
          ></textarea>
          <div class="input-footer">
            <span class="char-count" style="display: none;">{{ prompt.length }}/1000</span>
          </div>

          <!-- 선택된 태그 표시 영역 -->
          <SectionBox v-if="selectedTags.length > 0" variant="dark" :withShadow="true" :withBorder="true">
            <div class="selected-tags-container">
              <div class="selected-tags-list">
                <span v-for="tag in selectedTags" :key="tag" class="selected-tag">
                  {{ tag }}
                  <button @click="removeTag(tag)" class="remove-tag-btn">&times;</button>
                </span>
              </div>
              <button @click="clearAllTags" class="clear-all-btn">{{ $t('clear_tags') }}</button>
            </div>
          </SectionBox>
        </div>

        <!-- 태그 시스템 -->
        <SectionBox variant="dark">
          <div class="tags-container">
            <!-- 장소 태그 -->
            <div class="tag-category">
              <h4 class="category-title">{{ $t('place') }}</h4>
              <div class="tag-list">
                <button 
                  v-for="tag in locationTags" 
                  :key="tag"
                  @click="toggleTag(tag)"
                  class="tag-btn"
                  :class="{ 'tag-active': isTagActive(tag) }"
                >
                  {{ tag }}
                </button>
              </div>
            </div>

            <!-- 시간 태그 -->
            <div class="tag-category">
              <h4 class="category-title">{{ $t('time') }}</h4>
              <div class="tag-list">
                <button 
                  v-for="tag in timeTags" 
                  :key="tag"
                  @click="toggleTag(tag)"
                  class="tag-btn"
                  :class="{ 'tag-active': isTagActive(tag) }"
                >
                  {{ tag }}
                </button>
              </div>
            </div>

            <!-- 시점/구도 태그 -->
            <div class="tag-category">
              <h4 class="category-title">{{ $t('perspective') }}</h4>
              <div class="tag-list">
                <button 
                  v-for="tag in perspectiveTags" 
                  :key="tag"
                  @click="toggleTag(tag)"
                  class="tag-btn"
                  :class="{ 'tag-active': isTagActive(tag) }"
                >
                  {{ tag }}
                </button>
              </div>
            </div>

            <!-- 스타일 태그 -->
            <div class="tag-category">
              <h4 class="category-title">{{ $t('style') }}</h4>
              <div class="tag-list">
                <button 
                  v-for="tag in styleTags" 
                  :key="tag"
                  @click="toggleTag(tag)"
                  class="tag-btn"
                  :class="{ 'tag-active': isTagActive(tag) }"
                >
                  {{ tag }}
                </button>
              </div>
            </div>

            <!-- 분위기 태그 -->
            <div class="tag-category">
              <h4 class="category-title">{{ $t('mood') }}</h4>
              <div class="tag-list">
                <button 
                  v-for="tag in moodTags" 
                  :key="tag"
                  @click="toggleTag(tag)"
                  class="tag-btn"
                  :class="{ 'tag-active': isTagActive(tag) }"
                >
                  {{ tag }}
                </button>
              </div>
            </div>

            <!-- 조명 태그 -->
            <div class="tag-category">
              <h4 class="category-title">{{ $t('lighting') }}</h4>
              <div class="tag-list">
                <button 
                  v-for="tag in lightingTags" 
                  :key="tag"
                  @click="toggleTag(tag)"
                  class="tag-btn"
                  :class="{ 'tag-active': isTagActive(tag) }"
                >
                  {{ tag }}
                </button>
              </div>
            </div>
          </div>
        </SectionBox>
        
        <button 
          @click="generateImage" 
          :disabled="isLoading || !prompt.trim()"
          class="generate-btn"
        >
          <span v-if="!isLoading" class="btn-content">
            <span class="btn-icon">✨</span>
            {{ $t('generate_image') }}
          </span>
          <span v-else class="btn-content">
            <div class="btn-spinner"></div>
            {{ $t('generating') }}
          </span>
        </button>
      </div>

      <div v-if="error" class="error-message">
        <div class="error-icon">⚠️</div>
        <div class="error-content">
          <h4>{{ $t('error_occurred') }}</h4>
          <p>{{ error }}</p>
        </div>
      </div>

      <div v-if="isLoading" class="loading-section">
        <div class="loading-card">
          <div class="loading-animation">
            <div class="loading-circle"></div>
            <div class="loading-circle"></div>
            <div class="loading-circle"></div>
          </div>
          <h3>{{ $t('generating') }}</h3>
          <p>잠시만 기다려주세요...</p>
        </div>
      </div>

      <div v-if="imageUrl" class="result-section">
        <div class="result-header">
          <h3>🎉 {{ $t('generate_image') }}</h3>
          <p>아래 이미지를 확인하고 다운로드하세요</p>
        </div>
        
        <div class="image-container">
          <img :src="imageUrl" alt="Generated image" class="generated-image" />
          <div class="image-overlay">
            <button @click="downloadImage" class="download-btn">
              <span class="download-icon">⬇️</span>
              {{ $t('download') }}
            </button>
          </div>
        </div>
        
        <div class="action-buttons">
          <button @click="generateNewImage" class="new-image-btn">
            <span class="btn-icon">🔄</span>
            {{ $t('new_generate') }}
          </button>
        </div>
      </div>
    </SectionBox>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'
import SectionBox from './common/SectionBox.vue'

const prompt = ref('')
const imageUrl = ref('')
const isLoading = ref(false)
const error = ref('')
const selectedTags = ref<string[]>([])

// 태그 데이터를 i18n에서 가져오기
const { t, tm } = useI18n()

const getTagValues = (category: string) => {
  try {
    const tags = tm(`tags.${category}`);
    return Array.isArray(tags) ? tags : [];
  } catch (error) {
    console.error(`Error getting ${category} tags:`, error);
    return [];
  }
}

const locationTags = computed<string[]>(() => getTagValues('location'))
const timeTags = computed<string[]>(() => getTagValues('time'))
const perspectiveTags = computed<string[]>(() => getTagValues('perspective'))
const styleTags = computed<string[]>(() => getTagValues('style'))
const moodTags = computed<string[]>(() => getTagValues('mood'))
const lightingTags = computed<string[]>(() => getTagValues('lighting'))

// 태그 토글 함수
const toggleTag = (tag: string) => {
  const idx = selectedTags.value.indexOf(tag)
  if (idx === -1) {
    selectedTags.value.push(tag)
  } else {
    selectedTags.value.splice(idx, 1)
  }
  updatePrompt()
}

// 태그 제거 함수
const removeTag = (tag: string) => {
  const index = selectedTags.value.indexOf(tag)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
    updatePrompt()
  }
}

// 모든 태그 지우기
const clearAllTags = () => {
  selectedTags.value = []
  updatePrompt()
}

// 태그가 활성화되었는지 확인
const isTagActive = (tag: string) => {
  return selectedTags.value.includes(tag)
}

// 프롬프트 업데이트
const updatePrompt = () => {
  // 프롬프트에서 기존 [선택된 태그들: ...] 부분을 모두 제거
  let basePrompt = prompt.value.replace(/(,?\s*)?\[선택된 태그들: [^\]]*\]/g, '').trim()
  // 마지막에 남은 쉼표, 공백 제거
  basePrompt = basePrompt.replace(/(,|\s)+$/, '')
  if (selectedTags.value.length > 0) {
    prompt.value = basePrompt ? `${basePrompt}, [선택된 태그들: ${selectedTags.value.join(', ')}]` : `[선택된 태그들: ${selectedTags.value.join(', ')}]`
  } else {
    prompt.value = basePrompt
  }
}

const generateImage = async () => {
  if (!prompt.value.trim()) return
  
  isLoading.value = true
  error.value = ''
  imageUrl.value = ''
  
  try {
    const response = await axios.post('http://localhost:8000/generate-image', {
      prompt: prompt.value
    })
    
    imageUrl.value = response.data.image_url
  } catch (err: any) {
    error.value = err.response?.data?.detail || '이미지 생성 중 오류가 발생했습니다.'
    console.error('Error generating image:', err)
  } finally {
    isLoading.value = false
  }
}

const downloadImage = async () => {
  if (!imageUrl.value) return
  
  try {
    const response = await axios.get(imageUrl.value, { responseType: 'blob' })
    const url = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url
    link.download = `dalle-image-${Date.now()}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error('Error downloading image:', err)
    error.value = '이미지 다운로드 중 오류가 발생했습니다.'
  }
}

const generateNewImage = () => {
  prompt.value = ''
  imageUrl.value = ''
  error.value = ''
  selectedTags.value = []
}
</script>

<style scoped>
.dalle-container {
  max-width: 900px;
  margin: 0 auto;
}

.card-header h2 {
  font-size: 2.2rem;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.card-header p {
  font-size: 1rem;
  color: #a0aec0;
  margin: 0;
  font-weight: 400;
}

.input-section {
  margin-top: 20px;
}

.input-wrapper {
  margin-bottom: 25px;
}

.input-label {
  display: block;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 12px;
  font-size: 1.1rem;
}

.prompt-input {
  width: 100%;
  padding: 20px;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  font-size: 16px;
  resize: vertical;
  min-height: 120px;
  font-family: inherit;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.8);
  box-sizing: border-box;
}

.prompt-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  background: white;
}

.prompt-input::placeholder {
  color: #a0aec0;
  font-style: italic;
}

.input-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.char-count {
  font-size: 0.9rem;
  color: #718096;
}

/* 태그 시스템 스타일 */
.tags-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.tag-category {
  margin-bottom: 1.5rem;
  background: rgba(255, 255, 255, 0.9);
  padding: 1rem;
  border-radius: 16px;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.category-title {
  color: #2d3748;
  margin-bottom: 0.8rem;
  font-size: 1.1rem;
  font-weight: 600;
  text-shadow: none;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-btn {
  padding: 8px 16px;
  margin: 4px;
  border: none;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  color: #4a5568;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.9);
}

.tag-btn:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.tag-btn.tag-active {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transform: scale(1.05);
}

.selected-tags-container {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.selected-tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  flex: 1;
  min-height: 32px;
  align-items: center;
}

.selected-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  font-size: 0.9rem;
}

.remove-tag-btn {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0;
  font-size: 1.1rem;
  line-height: 1;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.remove-tag-btn:hover {
  opacity: 1;
}

.clear-all-btn {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 6px 12px;
  font-size: 0.9rem;
  opacity: 0.7;
  transition: opacity 0.2s;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.1);
  white-space: nowrap;
  flex-shrink: 0;
}

.clear-all-btn:hover {
  opacity: 1;
}

.generate-btn {
  width: 100%;
  padding: 18px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
}

.generate-btn:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.btn-icon {
  font-size: 1.2rem;
}

.btn-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background: linear-gradient(135deg, #fed7d7, #feb2b2);
  border: 1px solid #fc8181;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 30px;
  display: flex;
  align-items: flex-start;
  gap: 15px;
}

.error-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.error-content h4 {
  margin: 0 0 8px 0;
  color: #c53030;
  font-size: 1.1rem;
}

.error-content p {
  margin: 0;
  color: #742a2a;
  font-size: 0.95rem;
}

.loading-section {
  text-align: center;
  padding: 40px 20px;
}

.loading-card {
  background: rgba(102, 126, 234, 0.1);
  border-radius: 20px;
  padding: 40px;
  border: 2px dashed rgba(102, 126, 234, 0.3);
}

.loading-animation {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 20px;
}

.loading-circle {
  width: 12px;
  height: 12px;
  background: #667eea;
  border-radius: 50%;
  animation: bounce 1.4s ease-in-out infinite both;
}

.loading-circle:nth-child(1) { animation-delay: -0.32s; }
.loading-circle:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.loading-card h3 {
  color: #2d3748;
  margin: 0 0 10px 0;
  font-size: 1.3rem;
}

.loading-card p {
  color: #718096;
  margin: 0;
  font-size: 1rem;
}

.result-section {
  text-align: center;
}

.result-header {
  margin-bottom: 30px;
}

.result-header h3 {
  font-size: 2rem;
  color: #2d3748;
  margin: 0 0 10px 0;
  font-weight: 700;
}

.result-header p {
  color: #718096;
  margin: 0;
  font-size: 1.1rem;
}

.image-container {
  position: relative;
  margin-bottom: 30px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

.generated-image {
  width: 100%;
  height: auto;
  display: block;
  transition: transform 0.3s ease;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-container:hover .image-overlay {
  opacity: 1;
}

.image-container:hover .generated-image {
  transform: scale(1.02);
}

.download-btn {
  background: white;
  color: #2d3748;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.download-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.download-icon {
  font-size: 1.1rem;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.new-image-btn {
  background: linear-gradient(135deg, #48bb78, #38a169);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.new-image-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(72, 187, 120, 0.3);
}

@media (max-width: 768px) {
  .card {
    padding: 25px;
    margin: 0 10px;
  }
  
  .card-header {
    margin-bottom: 20px;
    padding-bottom: 20px;
  }
  
  .card-header h2 {
    font-size: 1.8rem;
  }
  
  .input-section {
    padding: 16px;
  }
  
  .prompt-input {
    padding: 15px;
    min-height: 100px;
  }
  
  .generate-btn {
    padding: 15px;
    font-size: 16px;
  }
  
  .action-buttons {
    flex-direction: column;
  }

  .tags-container {
    grid-template-columns: 1fr;
  }

  .tags-section {
    padding: 20px;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> 