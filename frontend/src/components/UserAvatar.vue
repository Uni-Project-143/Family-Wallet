<template>
  <div class="avatar" :class="sizeClass" :style="{ background: bgColor }" :title="displayName">
    <img
      v-if="avatarUrl && !imageError"
      :src="avatarUrl"
      :alt="displayName"
      class="avatar__img"
      @error="imageError = true"
    />
    <span v-else class="avatar__initials">{{ initials }}</span>
  </div>
</template>

<script setup>
  import { computed, ref, watch } from 'vue'

  const props = defineProps({
    avatarUrl: { type: String, default: null },
    fullName: { type: String, default: '' },
    email: { type: String, default: '' },
    size: { type: String, default: 'md' },
  })

  const imageError = ref(false)

  watch(
    () => props.avatarUrl,
    () => {
      imageError.value = false
    },
  )

  const displayName = computed(() => {
    if (props.fullName?.trim()) return props.fullName
    if (props.email?.trim()) return props.email
    return 'Без імені'
  })

  const initials = computed(() => {
    const name = displayName.value
    if (!name) return '?'
    return name
      .split(/[\s@.]+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((w) => w[0])
      .join('')
      .toUpperCase()
  })

  const sizeClass = computed(() => `avatar--${props.size}`)

  const bgColor = computed(() => {
    const palette = [
      'linear-gradient(135deg, #f2e9c8, #dfc876)',
      'linear-gradient(135deg, #f8d4c5, #e8a890)',
      'linear-gradient(135deg, #c5e0d4, #8fbfa3)',
      'linear-gradient(135deg, #cfd9e8, #8fa9c8)',
      'linear-gradient(135deg, #e8d4e3, #c498b9)',
      'linear-gradient(135deg, #d8ccc0, #a89486)',
    ]
    const key = (props.fullName || props.email || '?').toLowerCase()
    const hash = [...key].reduce((acc, ch) => acc + ch.charCodeAt(0), 0)
    return palette[hash % palette.length]
  })
</script>

<style scoped>
  .avatar {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    overflow: hidden;
    flex-shrink: 0;
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-weight: 700;
    color: #7a5e1a;
    user-select: none;
  }

  .avatar--sm {
    width: 32px;
    height: 32px;
    font-size: 11px;
  }
  .avatar--md {
    width: 40px;
    height: 40px;
    font-size: 14px;
  }
  .avatar--lg {
    width: 56px;
    height: 56px;
    font-size: 18px;
  }

  .avatar__img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .avatar__initials {
    letter-spacing: 0.5px;
  }
</style>
