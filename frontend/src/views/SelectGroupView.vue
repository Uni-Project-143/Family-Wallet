<template>
  <div class="page">
    <div class="page__inner">
      <h1 class="title">Choose a Family</h1>
      <p class="subtitle">
        You have several active families. Choose which one you want to join. You can switch between
        them at any time from the settings.
      </p>

      <div v-if="!groups.length" class="empty-state">
        <p>Failed to load the list of groups.</p>
        <button class="btn-secondary" @click="reloadGroups">Try Again</button>
      </div>

      <div v-else class="group-list">
        <button
          v-for="group in groups"
          :key="group.id"
          type="button"
          class="group-card"
          :class="{ 'group-card--admin': group.role === 'ADMIN' }"
          @click="enterGroup(group)"
        >
          <div class="group-card__avatar">
            {{ getGroupInitials(group.name) }}
          </div>
          <div class="group-card__body">
            <div class="group-card__name">{{ group.name }}</div>
            <div class="group-card__role">
              <span
                class="badge"
                :class="group.role === 'ADMIN' ? 'badge--admin' : 'badge--member'"
              >
                {{ group.role === 'ADMIN' ? 'Admin' : 'Member' }}
              </span>
              <span class="group-card__role-text">
                {{ group.role === 'ADMIN' ? 'You are an administrator' : 'You are a member' }}
              </span>
            </div>
          </div>
          <svg class="group-card__arrow" width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path
              d="M7 4L13 10L7 16"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </button>
      </div>

      <div class="page__footer">
        <router-link to="/group-setup" class="link-cta">
          + Create a new family or join an existing one
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuth } from '../composables/useAuth'
  import { fetchMyGroups } from '../services/authService'

  const router = useRouter()
  const { setActiveGroup } = useAuth()

  const groups = ref([])

  onMounted(() => {
    const passed = history.state?.groups
    if (Array.isArray(passed) && passed.length > 0) {
      groups.value = passed
    } else {
      reloadGroups()
    }
  })

  async function reloadGroups() {
    try {
      groups.value = await fetchMyGroups()
    } catch {
      // Не вдалося оновити список груп — залишаємо попередній стан
    }
  }

  function getGroupInitials(name) {
    return name
      .split(' ')
      .map((w) => w[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  function enterGroup(group) {
    setActiveGroup(group)
    router.push('/feed')
  }
</script>

<style scoped>
  .page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #faf8f3;
    padding: 24px;
  }

  .page__inner {
    width: 100%;
    max-width: 480px;
    background: #ffffff;
    border-radius: 16px;
    padding: 36px 32px;
    box-shadow: 0 8px 32px rgba(13, 12, 10, 0.06);
    border-top: 3px solid #b8973a;
  }

  .title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 26px;
    font-weight: 600;
    color: #0d0c0a;
    margin: 0 0 8px;
    text-align: center;
  }

  .subtitle {
    font-size: 13px;
    color: #6b6860;
    margin: 0 0 24px;
    line-height: 1.6;
    text-align: center;
  }

  .group-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .group-card {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 16px;
    background: #faf8f3;
    border: 1.5px solid #eae8e4;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.18s;
    font-family: 'DM Sans', system-ui, sans-serif;
    text-align: left;
  }

  .group-card:hover {
    border-color: #b8973a;
    background: #fbf7ec;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(184, 151, 58, 0.12);
  }

  .group-card--admin {
    border-color: #f2e9c8;
  }

  .group-card__avatar {
    width: 44px;
    height: 44px;
    border-radius: 10px;
    background: linear-gradient(135deg, #f2e9c8, #dfc876);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-weight: 700;
    font-size: 16px;
    color: #7a5e1a;
    flex-shrink: 0;
  }

  .group-card__body {
    flex: 1;
  }

  .group-card__name {
    font-size: 15px;
    font-weight: 600;
    color: #0d0c0a;
    margin-bottom: 4px;
  }

  .group-card__role {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .group-card__role-text {
    font-size: 11px;
    color: #6b6860;
  }

  .badge {
    display: inline-flex;
    align-items: center;
    height: 18px;
    padding: 0 7px;
    border-radius: 9999px;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
  }

  .badge--admin {
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    color: #ffffff;
  }

  .badge--member {
    background: #eae8e4;
    color: #6b6860;
  }

  .group-card__arrow {
    color: #b0ada7;
    flex-shrink: 0;
  }

  .empty-state {
    text-align: center;
    padding: 24px;
    color: #6b6860;
    font-size: 13px;
  }

  .btn-secondary {
    margin-top: 12px;
    height: 40px;
    padding: 0 18px;
    background: #ffffff;
    color: #6b6860;
    border: 1.5px solid #d6d3ce;
    border-radius: 8px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
  }

  .btn-secondary:hover {
    background: #f4f1e9;
    border-color: #b0ada7;
  }

  .page__footer {
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid #eae8e4;
    text-align: center;
  }

  .link-cta {
    font-size: 13px;
    font-weight: 600;
    color: #b8973a;
    text-decoration: none;
    transition: color 0.18s;
  }

  .link-cta:hover {
    color: #9b7a25;
  }

  @media (max-width: 560px) {
    .auth-card,
    .login-card,
    .register-card,
    .select-group-card {
      max-width: 100%;
      width: calc(100% - 32px);
      padding: 28px 22px;
    }
    .auth-title,
    .form-title {
      font-size: 24px;
    }
    .i-field {
      font-size: 16px;
    }
  }

  @media (max-width: 480px) {
    .group-option {
      padding: 14px 16px;
      gap: 12px;
    }
    .group-option__avatar {
      width: 44px;
      height: 44px;
      font-size: 18px;
    }
  }
</style>
