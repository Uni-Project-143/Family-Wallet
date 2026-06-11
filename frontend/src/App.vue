<template>
  <RouterView v-slot="{ Component, route }">
    <!-- Error Boundary на кожен маршрут: помилка рендеру однієї сторінки
         показує fallback, а не кладе весь застосунок. :key скидає boundary
         при переході на інший маршрут. -->
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

  // При старті застосунку з уже валідним токеном — синхронізуємо FCM-токен.
  onMounted(() => {
    if (localStorage.getItem('accessToken')) {
      initPush()
    }
  })
</script>
