<template>
  <RouterView />
</template>

<script setup>
  import { onMounted } from 'vue'
  import { usePushNotifications } from './composables/usePushNotifications'

  const { initPush } = usePushNotifications()

  // При старті застосунку з уже валідним токеном — синхронізуємо FCM-токен.
  onMounted(() => {
    if (localStorage.getItem('accessToken')) {
      initPush()
    }
  })
</script>
