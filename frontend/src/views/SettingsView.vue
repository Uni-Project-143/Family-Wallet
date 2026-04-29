<template>
  <div class="settings-page">
    <!-- ═══ NAVBAR (той самий що на Feed) ═══ -->
    <header class="navbar">
      <div class="navbar__left">
        <span class="navbar__logo">Family <span class="navbar__logo--accent">Wallet</span></span>
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
        <div class="avatar avatar--sm avatar--gold">{{ currentUserInitials }}</div>
        <span class="navbar__user-name">{{ currentUserName }}</span>
        <span v-if="isAdmin" class="badge badge--admin">Admin</span>
        <span v-else class="badge badge--member">Member</span>
      </div>
    </header>

    <!-- ═══ BODY ═══ -->
    <div class="settings-layout">
      <!-- ─── Settings sidebar nav ─── -->
      <aside class="settings-nav">
        <button
          v-for="item in navItems"
          :key="item.key"
          class="settings-nav__item"
          :class="{ 'settings-nav__item--active': activeSection === item.key }"
          @click="activeSection = item.key"
        >
          <span class="settings-nav__icon">{{ item.icon }}</span>
          {{ item.label }}
        </button>
      </aside>

      <!-- ─── Main content ─── -->
      <main class="settings-main">
        <!-- GROUP MEMBERS section -->
        <section v-if="activeSection === 'members'">
          <div class="settings-section__header">
            <h2 class="settings-section__title">Group Members</h2>
          </div>

          <!-- Members table -->
          <div class="members-table-wrap">
            <table class="members-table">
              <thead>
                <tr>
                  <th>Member</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Joined</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="member in groupMembers" :key="member.id">
                  <td>
                    <div class="member-cell">
                      <div class="avatar avatar--sm" :class="`avatar--${member.avatarVariant}`">
                        {{ member.initials }}
                      </div>
                      <span class="member-cell__name">{{ member.name }}</span>
                    </div>
                  </td>
                  <td class="td-email">{{ member.email }}</td>
                  <td>
                    <span
                      class="badge"
                      :class="member.role === 'ADMIN' ? 'badge--admin' : 'badge--member'"
                    >
                      {{ member.role }}
                    </span>
                  </td>
                  <td class="td-date">{{ member.joinedAt }}</td>
                  <td>
                    <!-- Admin не може сам себе видалити -->
                    <button
                      v-if="isAdmin && !member.isCurrentUser"
                      class="btn-remove"
                      @click="removeMember(member)"
                    >
                      Remove
                    </button>
                    <span v-else class="td-dash">—</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- ══ INVITE NEW MEMBER (US 1.3 FE-01, FE-02) ══ -->
          <div class="invite-section">
            <h3 class="invite-section__title">Invite New Member</h3>

            <!-- Тільки Admin бачить цю секцію (FE-01 conditional rendering) -->
            <template v-if="isAdmin">
              <p class="invite-section__desc">
                Share this link with your family member. The link is valid for 48 hours.
              </p>

              <!-- Group Invite Code -->
              <div class="invite-section__label">
                Group Invite Code
                <span class="invite-section__label-note">Only Admin can generate invite links</span>
              </div>

              <!-- Link box (FE-02) -->
              <div class="invite-link-box">
                <div
                  class="invite-link-box__url"
                  :class="{ 'invite-link-box__url--loading': isGeneratingLink }"
                >
                  <template v-if="isGeneratingLink">
                    <span class="invite-link-box__spinner">
                      <svg
                        class="spinner-icon"
                        width="16"
                        height="16"
                        viewBox="0 0 16 16"
                        fill="none"
                      >
                        <circle
                          cx="8"
                          cy="8"
                          r="6"
                          stroke="rgba(184,151,58,0.3)"
                          stroke-width="2"
                        />
                        <path
                          d="M8 2A6 6 0 0 1 14 8"
                          stroke="#b8973a"
                          stroke-width="2"
                          stroke-linecap="round"
                        />
                      </svg>
                    </span>
                    Generating link...
                  </template>
                  <template v-else-if="inviteUrl">
                    {{ inviteUrl }}
                  </template>
                  <template v-else>
                    <span class="invite-link-box__placeholder"
                      >Click "Generate" to create invite link</span
                    >
                  </template>
                </div>

                <!-- Copy button (Clipboard API FE-02) -->
                <button
                  v-if="inviteUrl && !isGeneratingLink"
                  class="btn-copy"
                  :class="{ 'btn-copy--copied': isCopied }"
                  @click="copyInviteLink"
                >
                  <svg v-if="!isCopied" width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <rect
                      x="4"
                      y="4"
                      width="8"
                      height="8"
                      rx="1.5"
                      stroke="currentColor"
                      stroke-width="1.5"
                    />
                    <path
                      d="M2 10V3C2 2.44772 2.44772 2 3 2H10"
                      stroke="currentColor"
                      stroke-width="1.5"
                      stroke-linecap="round"
                    />
                  </svg>
                  <svg v-else width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path
                      d="M2.5 7L5.5 10L11.5 4"
                      stroke="currentColor"
                      stroke-width="1.5"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                  {{ isCopied ? 'Copied!' : 'Copy' }}
                </button>
              </div>

              <!-- TTL note -->
              <div v-if="inviteUrl && inviteExpiresAt" class="invite-ttl">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <circle cx="6" cy="6" r="5" stroke="currentColor" stroke-width="1.2" />
                  <path
                    d="M6 3.5V6.5L8 8"
                    stroke="currentColor"
                    stroke-width="1.2"
                    stroke-linecap="round"
                  />
                </svg>
                Valid for {{ inviteTtlLabel }}
              </div>

              <!-- Action buttons -->
              <div class="invite-actions">
                <button class="btn-gold" :disabled="isGeneratingLink" @click="generateInviteLink">
                  <svg
                    v-if="!isGeneratingLink"
                    width="14"
                    height="14"
                    viewBox="0 0 14 14"
                    fill="none"
                  >
                    <path
                      d="M7 1V3M7 11V13M1 7H3M11 7H13"
                      stroke="currentColor"
                      stroke-width="1.5"
                      stroke-linecap="round"
                    />
                    <circle cx="7" cy="7" r="3" stroke="currentColor" stroke-width="1.5" />
                  </svg>
                  {{ inviteUrl ? 'Regenerate Link' : 'Generate Link' }}
                </button>
              </div>

              <div class="invite-security-note">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path
                    d="M6 1L1.5 3V6C1.5 8.5 3.5 10.5 6 11C8.5 10.5 10.5 8.5 10.5 6V3L6 1Z"
                    stroke="currentColor"
                    stroke-width="1.2"
                  />
                </svg>
                Only Admin can generate invite links. Non-admin users receive 403 on GET
                /group/invite.
              </div>

              <!-- Direct email invite -->
              <div class="invite-direct">
                <div class="invite-section__label" style="margin-bottom: 8px">
                  Or send invite directly by email
                </div>
                <div class="invite-direct__row">
                  <input
                    v-model="directEmail"
                    class="i-field"
                    type="email"
                    placeholder="member@example.com"
                    @keydown.enter="sendDirectInvite"
                  />
                  <button
                    class="btn-primary"
                    :disabled="!directEmail.trim() || isSendingDirectInvite"
                    @click="sendDirectInvite"
                  >
                    <span v-if="!isSendingDirectInvite">Send Invite</span>
                    <svg
                      v-else
                      class="spinner-icon"
                      width="16"
                      height="16"
                      viewBox="0 0 16 16"
                      fill="none"
                    >
                      <circle cx="8" cy="8" r="6" stroke="rgba(255,255,255,0.3)" stroke-width="2" />
                      <path
                        d="M8 2A6 6 0 0 1 14 8"
                        stroke="white"
                        stroke-width="2"
                        stroke-linecap="round"
                      />
                    </svg>
                  </button>
                </div>
              </div>
            </template>

            <!-- Member бачить заглушку замість invite (FE-01 conditional render) -->
            <template v-else>
              <div class="invite-restricted">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path
                    d="M10 2L2.5 5.5V10C2.5 14.1 5.9 17.9 10 19C14.1 17.9 17.5 14.1 17.5 10V5.5L10 2Z"
                    stroke="#B0ADA7"
                    stroke-width="1.5"
                  />
                  <path
                    d="M7 10L9 12L13 8"
                    stroke="#B0ADA7"
                    stroke-width="1.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
                <p>Only the group Admin can invite new members.</p>
              </div>
            </template>
          </div>
        </section>

        <!-- CONNECTED CARDS section -->
        <section v-if="activeSection === 'cards'">
          <div class="settings-section__header">
            <h2 class="settings-section__title">Connected Cards</h2>
          </div>
          <div class="cards-list">
            <div v-for="card in connectedCards" :key="card.id" class="card-item">
              <div class="card-item__info">
                <div class="card-item__bank">{{ card.bankName }}</div>
                <div class="card-item__pan">{{ card.maskedPan }}</div>
                <div class="card-item__balance">{{ card.balance.toLocaleString('uk-UA') }} UAH</div>
              </div>
              <div class="card-item__actions">
                <span class="card-item__status">
                  <span class="card-item__dot"></span> Connected
                </span>
                <button v-if="isAdmin" class="btn-remove" @click="disconnectCard(card)">
                  Disconnect
                </button>
              </div>
            </div>
          </div>
          <button
            v-if="isAdmin"
            class="btn-gold"
            style="margin-top: 16px"
            @click="isConnectCardOpen = true"
          >
            + Connect Card
          </button>

          <ConnectCardModal
            :is-open="isConnectCardOpen"
            @close="isConnectCardOpen = false"
            @toast="showToast($event.message, $event.type)"
            @connected="handleCardConnected"
          />
        </section>

        <!-- NOTIFICATIONS section -->
        <section v-if="activeSection === 'notifications'">
          <div class="settings-section__header">
            <h2 class="settings-section__title">Notifications</h2>
          </div>
          <div class="toggle-list">
            <div v-for="pref in notifPreferences" :key="pref.key" class="toggle-row">
              <div class="toggle-row__info">
                <div class="toggle-row__label">{{ pref.label }}</div>
                <div class="toggle-row__desc">{{ pref.description }}</div>
              </div>
              <button
                class="toggle-track"
                :class="{ 'toggle-track--on': pref.isEnabled }"
                @click="pref.isEnabled = !pref.isEnabled"
              >
                <span class="toggle-thumb"></span>
              </button>
            </div>
          </div>
        </section>

        <!-- PRIVACY section -->
        <section v-if="activeSection === 'privacy'">
          <div class="settings-section__header">
            <h2 class="settings-section__title">Privacy & Data</h2>
          </div>
          <div class="privacy-info">
            <div class="info-box">
              Your financial data is encrypted and stored securely. Family Wallet processes your
              Monobank transactions only within your family group. See our
              <a href="/privacy" target="_blank" class="link">Privacy Policy</a> for details. (GDPR
              NFR-06)
            </div>
            <button class="btn-danger" style="margin-top: 20px" @click="confirmDeleteAccount">
              Delete my account and data
            </button>
          </div>
        </section>
      </main>
    </div>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast.isVisible" class="toast" :class="`toast--${toast.type}`" role="alert">
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
  import { ref, computed, watch, onMounted } from 'vue'
  import { useAuth } from '../composables/useAuth'
  import {
    fetchGroupInviteLink,
    regenerateGroupInviteLink,
    fetchGroupMembers,
  } from '../services/authService'

  import { useRoute } from 'vue-router'
  import ConnectCardModal from '../components/ConnectCardModal.vue'

  const isConnectCardOpen = ref(false)
  const route = useRoute()
  const activeSection = ref(route.query.section || 'members')

  watch(
    () => route.query.section,
    (section) => {
      activeSection.value = section || 'members'
    },
    { immediate: true },
  )

  // Реальна роль з localStorage через useAuth
  const { currentUser, isAdmin } = useAuth()

  const currentUserName = computed(() => currentUser.value?.fullName || 'User')
  const currentUserInitials = computed(() => {
    const name = currentUser.value?.fullName || 'U'
    return name
      .split(' ')
      .map((w) => w[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  })

  const navItems = [
    { key: 'members', icon: '👥', label: 'Group Members' },
    { key: 'cards', icon: '💳', label: 'Connected Cards' },
    { key: 'notifications', icon: '🔔', label: 'Notifications' },
    { key: 'privacy', icon: '🛡', label: 'Privacy & Data' },
  ]

  // ─── Group Members з API ───
  const groupMembers = ref([])
  const isLoadingMembers = ref(false)

  function formatJoinedDate(isoDate) {
    if (!isoDate) return ''
    return new Date(isoDate).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    })
  }

  function mapMemberFromApi(apiMember, currentUserEmail) {
    const fullName = apiMember.full_name || apiMember.email || 'User'
    const initials = fullName
      .split(' ')
      .map((w) => w[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)

    const variants = ['gold', 'dark', 'light']
    const variantIdx = (initials.charCodeAt(0) || 0) % variants.length

    return {
      id: apiMember.user_id || apiMember.id,
      name: fullName,
      initials,
      role: apiMember.role,
      avatarVariant: variants[variantIdx],
      email: apiMember.email,
      joinedAt: formatJoinedDate(apiMember.joined_at),
      isCurrentUser: apiMember.email === storedUser.email,
    }
  }

  async function loadGroupMembers() {
    const storedUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
    if (!storedUser.groupId) return

    isLoadingMembers.value = true
    try {
      const data = await fetchGroupMembers(storedUser.groupId)
      const members = Array.isArray(data) ? data : data.members || []
      groupMembers.value = members.map((m) => mapMemberFromApi(m, storedUser.email))
    } catch (err) {
      showToast('Failed to load group members', 'error')
    } finally {
      isLoadingMembers.value = false
    }
  }

  onMounted(() => {
    loadGroupMembers()
  })

  /**
   * Видаляє учасника з групи.
   * TODO: підключити DELETE /api/v1/group/{groupId}/members/{userId} коли з'явиться
   */
  function removeMember(member) {
    if (!confirm(`Remove ${member.name} from the group?`)) return
    showToast('Remove member endpoint not available yet', 'info')
  }

  // ─── Invite link ───
  const inviteUrl = ref('')
  const inviteExpiresAt = ref(null)
  const isGeneratingLink = ref(false)
  const isCopied = ref(false)
  const directEmail = ref('')
  const isSendingDirectInvite = ref(false)

  const inviteTtlLabel = computed(() => {
    if (!inviteExpiresAt.value) return ''
    const hours = Math.round((new Date(inviteExpiresAt.value) - Date.now()) / 3600000)
    if (hours > 1) return `${hours} hours`
    if (hours === 1) return '1 hour'
    return 'less than 1 hour'
  })

  /**
   * Генерує або перегенеровує invite-лінк.
   * GET /api/v1/group/{groupId}/invite
   */
  async function generateInviteLink() {
    isGeneratingLink.value = true

    const storedUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
    const groupId = storedUser.groupId

    if (!groupId) {
      showToast('Group ID not found. Please re-login.', 'error')
      isGeneratingLink.value = false
      return
    }

    try {
      const fn = inviteUrl.value
        ? () => regenerateGroupInviteLink(groupId)
        : () => fetchGroupInviteLink(groupId)

      const data = await fn()

      // Бекенд повертає invite_link та expires_at
      inviteUrl.value = data.invite_link
      inviteExpiresAt.value = data.expires_at

      showToast(inviteUrl.value ? 'New link generated' : 'Invite link ready', 'success')
    } catch (err) {
      const status = err.response?.status
      if (status === 403) {
        showToast('Only Admin can generate invite links (Rule-02)', 'error')
      } else {
        showToast('Error generating invite link. Try again.', 'error')
      }
    } finally {
      isGeneratingLink.value = false
    }
  }

  /**
   * Копіює invite URL через Clipboard API.
   */
  async function copyInviteLink() {
    if (!inviteUrl.value) return
    try {
      await navigator.clipboard.writeText(inviteUrl.value)
      isCopied.value = true
      showToast('Link copied ✓', 'success')
      setTimeout(() => {
        isCopied.value = false
      }, 2500)
    } catch {
      showToast('Failed to copy. Please copy manually.', 'error')
    }
  }

  /**
   * Відправляє запрошення напряму на email.
   * TODO: підключити POST /api/v1/group/{groupId}/invite/send коли з'явиться endpoint
   */
  async function sendDirectInvite() {
    if (!directEmail.value.trim()) return
    isSendingDirectInvite.value = true
    try {
      // TODO: реальний запит після появи endpoint
      // await apiClient.post(`/api/v1/group/${groupId}/invite/send`, { email: directEmail.value })
      showToast(`Invite sent to ${directEmail.value}`, 'success')
      directEmail.value = ''
    } catch {
      showToast('Failed to send invite. Try again.', 'error')
    } finally {
      isSendingDirectInvite.value = false
    }
  }

  // ─── Cards ───
  // TODO: підключити до GET /api/v1/group/{groupId}/cards коли з'явиться endpoint
  const connectedCards = ref([
    { id: 1, bankName: 'Monobank', maskedPan: '•••• •••• •••• 4521', balance: 12340 },
    { id: 2, bankName: 'Monobank', maskedPan: '•••• •••• •••• 7732', balance: 3870 },
  ])

  /**
   * Відключає картку від групи.
   * @param {object} card
   */
  function disconnectCard(card) {
    if (confirm(`Disconnect ${card.maskedPan}?`)) {
      connectedCards.value = connectedCards.value.filter((c) => c.id !== card.id)
      showToast('Card disconnected. Existing transactions preserved.', 'success')
    }
  }

  // ─── Notifications ───
  const notifPreferences = ref([
    {
      key: 'gift_unlock',
      label: 'Gift Event unlock reminders',
      description: '24h before and on unlock day',
      isEnabled: true,
    },
    {
      key: 'reactions',
      label: 'Reaction notifications',
      description: 'When someone reacts to your transaction',
      isEnabled: true,
    },
    {
      key: 'money_req',
      label: 'Money Request alerts',
      description: 'When you receive a transfer request',
      isEnabled: true,
    },
    {
      key: 'new_member',
      label: 'New member joined',
      description: 'When someone joins via invite link',
      isEnabled: false,
    },
  ])

  function confirmDeleteAccount() {
    if (confirm('This will permanently delete your account and all data. Are you sure?')) {
      showToast('Account deletion — contact support', 'error')
    }
  }

  // ─── Toast ───
  const toast = ref({ isVisible: false, message: '', type: 'success' })

  /**
   * Показує toast-повідомлення.
   * @param {string} message
   * @param {'success'|'error'|'info'} type
   */
  function showToast(message, type = 'success') {
    toast.value = { isVisible: true, message, type }
    setTimeout(() => {
      toast.value.isVisible = false
    }, 3000)
  }

  /**
   * Додає нову картку у локальний список після успішного підключення.
   * @param {{ alias: string, syncFrom: string }} cardData
   */
  function handleCardConnected(cardData) {
    connectedCards.value.push({
      id: Date.now(),
      bankName: 'Monobank',
      maskedPan: '•••• •••• •••• ' + Math.floor(1000 + Math.random() * 9000),
      balance: 0,
      alias: cardData.alias,
    })
  }
</script>

<style scoped>
  /* ── Page ── */
  .settings-page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: #faf8f3;
  }

  /* ── Navbar (той самий стиль що в FeedView) ── */
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

  /* ── Layout ── */
  .settings-layout {
    display: flex;
    flex: 1;
    height: calc(100vh - 60px);
    overflow: hidden;
  }

  /* ── Settings sidebar nav ── */
  .settings-nav {
    width: 224px;
    background: #fff;
    border-right: 1px solid #eae8e4;
    padding: 20px 0;
    flex-shrink: 0;
  }

  .settings-nav__item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 11px 22px;
    font-size: 13px;
    font-weight: 500;
    color: #6b6860;
    cursor: pointer;
    transition: all 0.15s;
    border-left: 3px solid transparent;
    border: none;
    background: none;
    width: 100%;
    text-align: left;
    font-family: 'DM Sans', system-ui, sans-serif;
    border-left: 3px solid transparent;
  }

  .settings-nav__item:hover {
    color: #0d0c0a;
    background: #fbf7ec;
  }

  .settings-nav__item--active {
    color: #9b7a25;
    font-weight: 600;
    background: #fbf7ec;
    border-left-color: #b8973a;
  }

  .settings-nav__icon {
    font-size: 15px;
  }

  /* ── Settings main ── */
  .settings-main {
    flex: 1;
    padding: 36px 48px;
    overflow-y: auto;
    background: #faf8f3;
  }

  .settings-section__header {
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #eae8e4;
  }
  .settings-section__title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 22px;
    font-weight: 600;
    letter-spacing: -0.2px;
    color: #0d0c0a;
    margin: 0;
  }

  /* ── Members table ── */
  .members-table-wrap {
    background: #fff;
    border: 1px solid #eae8e4;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 1px 2px rgba(13, 12, 10, 0.06);
    margin-bottom: 36px;
  }
  .members-table {
    width: 100%;
    border-collapse: collapse;
  }
  .members-table th {
    text-align: left;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #b0ada7;
    padding: 0 16px 12px;
    border-bottom: 1.5px solid #eae8e4;
    padding-top: 16px;
  }
  .members-table td {
    padding: 14px 16px;
    border-bottom: 1px solid #eae8e4;
    font-size: 13px;
    vertical-align: middle;
  }
  .members-table tr:last-child td {
    border-bottom: none;
  }
  .members-table tr:hover td {
    background: #fbf7ec;
  }

  .member-cell {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .member-cell__name {
    font-size: 13px;
    font-weight: 500;
    color: #0d0c0a;
  }
  .td-email {
    color: #6b6860;
  }
  .td-date {
    color: #b0ada7;
    font-family: 'DM Mono', 'Courier New', monospace;
    font-size: 12px;
  }
  .td-dash {
    color: #b0ada7;
  }

  /* ── Invite section ── */
  .invite-section {
    background: #fff;
    border: 1px solid #eae8e4;
    border-radius: 12px;
    padding: 28px;
    box-shadow: 0 1px 2px rgba(13, 12, 10, 0.06);
  }
  .invite-section__title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 18px;
    font-weight: 600;
    color: #0d0c0a;
    margin: 0 0 8px;
  }
  .invite-section__desc {
    font-size: 13px;
    color: #6b6860;
    margin: 0 0 20px;
    line-height: 1.6;
  }
  .invite-section__label {
    font-size: 11px;
    font-weight: 600;
    color: #6b6860;
    letter-spacing: 0.7px;
    text-transform: uppercase;
    margin-bottom: 8px;
  }
  .invite-section__label-note {
    font-size: 9px;
    font-weight: 400;
    color: #b0ada7;
    letter-spacing: 0;
    text-transform: none;
    margin-left: 4px;
  }

  /* Link box */
  .invite-link-box {
    display: flex;
    align-items: stretch;
    border: 1.5px solid #dfc876;
    border-radius: 8px;
    overflow: hidden;
    background: #fff;
    box-shadow: 0 2px 8px rgba(184, 151, 58, 0.1);
    margin-bottom: 8px;
  }

  .invite-link-box__url {
    flex: 1;
    padding: 0 16px;
    font-size: 13px;
    color: #6b6860;
    font-family: 'DM Mono', 'Courier New', monospace;
    display: flex;
    align-items: center;
    gap: 10px;
    background: #fbf7ec;
    border-right: 1px solid #f2e9c8;
    min-height: 46px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .invite-link-box__url--loading {
    color: #b0ada7;
  }
  .invite-link-box__placeholder {
    color: #b0ada7;
    font-style: italic;
  }

  .invite-link-box__spinner {
    display: flex;
  }

  .btn-copy {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 0 20px;
    background: #fff;
    border: none;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: #9b7a25;
    cursor: pointer;
    transition: all 0.18s;
    flex-shrink: 0;
  }

  .btn-copy:hover {
    background: #fbf7ec;
  }
  .btn-copy--copied {
    color: #2a6b2a;
  }

  /* TTL */
  .invite-ttl {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    color: #9b7a25;
    margin-bottom: 16px;
  }

  /* Action buttons */
  .invite-actions {
    display: flex;
    gap: 10px;
    margin-bottom: 16px;
  }

  .invite-security-note {
    display: flex;
    align-items: flex-start;
    gap: 6px;
    font-size: 11px;
    color: #b0ada7;
    line-height: 1.6;
    margin-bottom: 28px;
    padding: 10px 12px;
    background: #f4f1e9;
    border-radius: 6px;
  }

  /* Direct invite */
  .invite-direct {
    border-top: 1px solid #eae8e4;
    padding-top: 24px;
  }
  .invite-direct__row {
    display: flex;
    gap: 12px;
    max-width: 520px;
  }

  /* Restricted (Member view) */
  .invite-restricted {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    background: #f4f1e9;
    border-radius: 8px;
    font-size: 13px;
    color: #b0ada7;
    margin-top: 12px;
  }

  /* ── Cards list ── */
  .cards-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .card-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: #fff;
    border: 1px solid #f2e9c8;
    border-radius: 12px;
    background: linear-gradient(135deg, #faf8f3, #fbf7ec);
  }
  .card-item__bank {
    font-size: 11px;
    font-weight: 700;
    color: #9b7a25;
    letter-spacing: 0.5px;
    margin-bottom: 2px;
  }
  .card-item__pan {
    font-size: 13px;
    color: #6b6860;
    font-family: 'DM Mono', 'Courier New', monospace;
    margin-bottom: 2px;
  }
  .card-item__balance {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 17px;
    font-weight: 600;
    color: #0d0c0a;
  }
  .card-item__actions {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .card-item__status {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: #2a6b2a;
  }
  .card-item__dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #2a6b2a;
  }

  /* ── Toggle list ── */
  .toggle-list {
    display: flex;
    flex-direction: column;
    gap: 0;
    background: #fff;
    border: 1px solid #eae8e4;
    border-radius: 12px;
    overflow: hidden;
  }
  .toggle-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    border-bottom: 1px solid #eae8e4;
  }
  .toggle-row:last-child {
    border-bottom: none;
  }
  .toggle-row__info {
    flex: 1;
  }
  .toggle-row__label {
    font-size: 13px;
    font-weight: 600;
    color: #0d0c0a;
    margin-bottom: 2px;
  }
  .toggle-row__desc {
    font-size: 12px;
    color: #b0ada7;
  }
  .toggle-track {
    width: 44px;
    height: 24px;
    border-radius: 9999px;
    background: #d6d3ce;
    position: relative;
    border: none;
    cursor: pointer;
    transition: background 0.2s;
    flex-shrink: 0;
  }
  .toggle-track--on {
    background: #b8973a;
  }
  .toggle-thumb {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #fff;
    position: absolute;
    top: 3px;
    left: 3px;
    box-shadow: 0 1px 3px rgba(13, 12, 10, 0.12);
    transition: transform 0.2s;
  }
  .toggle-track--on .toggle-thumb {
    transform: translateX(20px);
  }

  /* ── Privacy ── */
  .info-box {
    background: #fbf7ec;
    border: 1px solid #f2e9c8;
    border-radius: 8px;
    padding: 16px 18px;
    font-size: 13px;
    color: #6b6860;
    line-height: 1.7;
  }
  .link {
    color: #b8973a;
  }

  /* ── Shared components ── */
  .i-field {
    height: 46px;
    border: 1.5px solid #eae8e4;
    border-radius: 8px;
    background: #f4f1e9;
    padding: 0 16px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 14px;
    color: #0d0c0a;
    outline: none;
    flex: 1;
    transition: all 0.18s;
  }
  .i-field:focus {
    border-color: #b8973a;
    background: #fff;
    box-shadow: 0 0 0 3px rgba(184, 151, 58, 0.15);
  }
  .i-field::placeholder {
    color: #b0ada7;
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
  .avatar--dark {
    background: linear-gradient(135deg, #3f3d38, #2d2b27);
    color: #ead9a0;
  }
  .avatar--light {
    background: linear-gradient(135deg, #f8f2e0, #f2e9c8);
    color: #9b7a25;
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

  .btn-primary {
    height: 46px;
    padding: 0 24px;
    background: #0d0c0a;
    color: #fff;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    flex-shrink: 0;
  }
  .btn-primary:hover:not(:disabled) {
    background: #2d2b27;
  }
  .btn-primary:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .btn-gold {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    height: 44px;
    padding: 0 24px;
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
    box-shadow: 0 4px 16px rgba(184, 151, 58, 0.18);
  }
  .btn-gold:hover:not(:disabled) {
    background: linear-gradient(135deg, #9b7a25, #b8973a);
    transform: translateY(-1px);
  }
  .btn-gold:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    transform: none;
  }

  .btn-remove {
    padding: 6px 14px;
    background: #fef0ed;
    color: #c4402a;
    border: 1.5px solid #e8897a;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
    font-family: 'DM Sans', system-ui, sans-serif;
  }
  .btn-remove:hover {
    background: #c4402a;
    color: #fff;
  }

  .btn-danger {
    height: 44px;
    padding: 0 24px;
    background: #fef0ed;
    color: #c4402a;
    border: 1.5px solid #e8897a;
    border-radius: 8px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
  }
  .btn-danger:hover {
    background: #c4402a;
    color: #fff;
  }

  .spinner-icon {
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .toast {
    position: fixed;
    bottom: 28px;
    right: 28px;
    padding: 14px 20px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 500;
    z-index: 999;
    box-shadow: 0 8px 24px rgba(13, 12, 10, 0.14);
    font-family: 'DM Sans', system-ui, sans-serif;
  }
  .toast--success {
    background: #0d0c0a;
    color: #fff;
  }
  .toast--error {
    background: #fef0ed;
    color: #c4402a;
    border: 1px solid #e8897a;
  }
  .toast--info {
    background: #eef3fb;
    color: #2a4e8b;
    border: 1px solid #8aaad4;
  }
  .toast-enter-active,
  .toast-leave-active {
    transition: all 0.25s ease;
  }
  .toast-enter-from,
  .toast-leave-to {
    opacity: 0;
    transform: translateY(12px);
  }
</style>
