<template>
  <header class="navbar">
    <div class="navbar__left">
      <span class="navbar__logo">Family <span class="navbar__logo--accent">Wallet</span></span>
      <slot name="left" />
    </div>

    <nav class="navbar__center">
      <router-link to="/feed" class="navbar__tab" active-class="navbar__tab--active"
        >Feed</router-link
      >
      <router-link to="/gift-events" class="navbar__tab" active-class="navbar__tab--active"
        >Gift Events</router-link
      >
      <router-link to="/settings" class="navbar__tab" active-class="navbar__tab--active"
        >Settings</router-link
      >
    </nav>

    <div class="navbar__right">
      <div class="avatar avatar--sm avatar--gold">{{ initials }}</div>
      <span class="navbar__user-name">{{ fullName }}</span>
      <span v-if="isAdmin" class="badge badge--admin">Admin</span>
      <span v-else class="badge badge--member">Member</span>

      <button
        v-if="showLogout"
        class="logout-btn"
        :disabled="isLoading"
        aria-label="Logout"
        @click="handleLogout"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path
            d="M6 14H3.5C2.67 14 2 13.33 2 12.5V3.5C2 2.67 2.67 2 3.5 2H6"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
          />
          <path
            d="M11 11L14 8L11 5M14 8H6"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </button>
    </div>
  </header>
</template>

<script setup>
  import { computed } from 'vue'
  import { useAuth } from '../composables/useAuth'

  defineProps({
    showLogout: { type: Boolean, default: false },
  })

  const { currentUser, isAdmin, isLoading, logout } = useAuth()

  const fullName = computed(() => currentUser.value?.fullName || '')
  const initials = computed(() => {
    const name = currentUser.value?.fullName || '?'
    if (!name) return '?'
    return name
      .split(' ')
      .map((w) => w[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  })

  async function handleLogout() {
    await logout()
  }
</script>

<style scoped>
  .navbar {
    height: 60px;
    background: #0d0c0a;
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    padding: 0 28px;
    flex-shrink: 0;
    border-bottom: 1px solid rgba(184, 151, 58, 0.18);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .navbar__left {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .navbar__logo {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 18px;
    font-weight: 600;
    color: #fff;
    white-space: nowrap;
  }
  .navbar__logo--accent {
    color: #b8973a;
  }

  .navbar__center {
    display: flex;
    gap: 2px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 4px;
    justify-self: center;
  }
  .navbar__tab {
    padding: 7px 20px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.5);
    text-decoration: none;
    transition: all 0.18s;
    white-space: nowrap;
    border: 1px solid transparent;
  }
  .navbar__tab:hover {
    color: rgba(255, 255, 255, 0.85);
  }
  .navbar__tab--active {
    background: rgba(184, 151, 58, 0.18);
    color: #ead9a0;
    font-weight: 600;
    border-color: rgba(184, 151, 58, 0.25);
  }

  .navbar__right {
    display: flex;
    align-items: center;
    gap: 10px;
    justify-self: end;
  }
  .navbar__user-name {
    font-size: 13px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.85);
  }

  .logout-btn {
    width: 32px;
    height: 32px;
    border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: rgba(255, 255, 255, 0.04);
    color: rgba(255, 255, 255, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.18s;
    margin-left: 4px;
  }
  .logout-btn:hover:not(:disabled) {
    background: rgba(196, 64, 42, 0.18);
    border-color: rgba(196, 64, 42, 0.4);
    color: #ff8a72;
  }
  .logout-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .avatar {
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-weight: 700;
    flex-shrink: 0;
  }
  .avatar--sm {
    width: 32px;
    height: 32px;
    font-size: 11px;
  }
  .avatar--gold {
    background: linear-gradient(135deg, #f2e9c8, #dfc876);
    color: #7a5e1a;
  }

  .badge {
    display: inline-flex;
    align-items: center;
    height: 20px;
    padding: 0 8px;
    border-radius: 9999px;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
  }
  .badge--admin {
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    color: #fff;
    box-shadow: 0 2px 6px rgba(184, 151, 58, 0.25);
  }
  .badge--member {
    background: #eae8e4;
    color: #6b6860;
    border: 1px solid #d6d3ce;
  }

  @media (max-width: 768px) {
    .navbar {
      grid-template-columns: 1fr auto;
      grid-template-rows: auto auto;
      height: auto;
      padding: 10px 14px;
      gap: 8px 10px;
    }
    .navbar__left {
      grid-row: 1;
      grid-column: 1;
    }
    .navbar__right {
      grid-row: 1;
      grid-column: 2;
      gap: 6px;
    }
    .navbar__center {
      grid-row: 2;
      grid-column: 1 / -1;
      justify-self: center;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
    }
    .navbar__center::-webkit-scrollbar {
      display: none;
    }
    .navbar__logo {
      font-size: 15px;
    }
    .navbar__tab {
      padding: 11px 22px;
      font-size: 13px;
    }
    .navbar__user-name {
      display: none;
    }
  }

  @media (max-width: 480px) {
    .navbar {
      padding: 8px 12px;
    }
    .navbar__tab {
      padding: 10px 20px;
      font-size: 12px;
    }
  }
</style>
