<template>
  <RouterView v-slot="{ Component, route }">
    <ErrorBoundary :key="route.fullPath">
      <component :is="Component" />
    </ErrorBoundary>
  </RouterView>
</template>

<script setup>
  import { onMounted } from 'vue'
  import { usePushNotifications } from './composables/usePushNotifications'
  import ErrorBoundary from './components/ErrorBoundary.vue'

  const { initPush } = usePushNotifications()

  onMounted(() => {
    if (localStorage.getItem('accessToken')) {
      initPush()
    }
  })
</script>
