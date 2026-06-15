<template>
  <div class="settings-page">
    <NavBar />

    <div class="settings-layout">
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

      <main class="settings-main">
        <section v-if="activeSection === 'members'">
          <div class="settings-section__header">
            <h2 class="settings-section__title">Group Members</h2>
          </div>

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
                  <td data-label="Member">
                    <div class="member-cell">
                      <div class="avatar avatar--sm" :class="`avatar--${member.avatarVariant}`">
                        {{ member.initials }}
                      </div>
                      <span class="member-cell__name">{{ member.name }}</span>
                    </div>
                  </td>
                  <td data-label="Email" class="td-email">{{ member.email }}</td>
                  <td data-label="Role">
                    <span
                      class="badge"
                      :class="member.role === 'ADMIN' ? 'badge--admin' : 'badge--member'"
                    >
                      {{ member.role }}
                    </span>
                  </td>
                  <td data-label="Joined" class="td-date">{{ member.joinedAt }}</td>
                  <td data-label="Actions">
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

          <div class="invite-section">
            <h3 class="invite-section__title">Invite New Member</h3>

            <template v-if="isAdmin">
              <p class="invite-section__desc">
                Share this link with your family member. The link is valid for 48 hours.
              </p>

              <div class="invite-section__label">
                Group Invite Code
                <span class="invite-section__label-note">Only Admin can generate invite links</span>
              </div>

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

        <section v-if="activeSection === 'cards'">
          <div class="settings-section__header">
            <h2 class="settings-section__title">Connected Cards</h2>
          </div>

          <div v-if="isLoadingCards" class="cards-loading">
            <div class="card-skeleton"></div>
            <div class="card-skeleton"></div>
          </div>

          <div v-else-if="connectedCards.length === 0" class="cards-empty">
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
              <rect
                x="4"
                y="10"
                width="32"
                height="22"
                rx="3"
                stroke="#d6d3ce"
                stroke-width="1.5"
              />
              <path d="M4 16H36" stroke="#d6d3ce" stroke-width="1.5" />
            </svg>
            <p>No cards connected yet.</p>
            <span>Connect your Monobank card to start tracking family expenses automatically.</span>
          </div>

          <div v-else class="cards-list">
            <div v-for="card in connectedCards" :key="card.id" class="card-item">
              <div class="card-item__icon">
                <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
                  <rect x="2" y="5" width="18" height="13" rx="2" fill="#0d0c0a" />
                  <rect x="2" y="8" width="18" height="2" fill="#b8973a" />
                </svg>
              </div>

              <div class="card-item__info">
                <div class="card-item__bank">Monobank</div>
                <div class="card-item__pan">{{ card.masked_pan }}</div>
                <div v-if="card.owner_full_name" class="card-item__owner">
                  {{ card.owner_full_name }}
                </div>
              </div>

              <div class="card-item__actions">
                <span class="card-item__status">
                  <span class="card-item__dot"></span>
                  {{ card.status }}
                </span>
                <button class="btn-details" @click="openCardDetails(card)">Details</button>
                <button v-if="isOwnCard(card)" class="btn-remove" @click="askDisconnect(card)">
                  Disconnect
                </button>
              </div>
            </div>
          </div>

          <button class="btn-gold" style="margin-top: 16px" @click="isConnectCardOpen = true">
            + Connect Card
          </button>

          <ConnectCardModal
            :is-open="isConnectCardOpen"
            @close="isConnectCardOpen = false"
            @toast="showToast($event.message, $event.type)"
            @connected="handleCardConnected"
          />

          <ConfirmDialog
            :is-open="isConfirmOpen"
            title="Disconnect this card?"
            :message="
              cardToDisconnect
                ? `New transactions from ${cardToDisconnect.masked_pan} will not be synced. Existing transaction history will be preserved.`
                : ''
            "
            confirm-text="Yes, disconnect"
            cancel-text="Keep card"
            variant="danger"
            :is-loading="isDisconnecting"
            @confirm="confirmDisconnect"
            @cancel="cancelDisconnect"
          />
          <CardDetailsModal
            :is-open="isCardDetailsOpen"
            :card="selectedCardForDetails"
            @close="closeCardDetails"
          />
        </section>

        <section v-if="activeSection === 'notifications'">
          <div class="settings-section__header">
            <h2 class="settings-section__title">Notifications</h2>
          </div>
          <div class="privacy-info">
            <div class="info-box">Family Wallet keeps you informed in two ways:</div>

            <div class="notif-type">
              <div class="notif-type__title">🎁 Secret Gift — push &amp; email</div>
              <div class="notif-type__desc">
                A reminder 24 hours before a gift unlocks, a reminder on the unlock day, and a
                notification the moment the gift is revealed. Browser push requires granting
                notification permission; you always see these in your in-app notifications as well.
              </div>
            </div>

            <div class="notif-type">
              <div class="notif-type__title">⚡ Real-time feed updates</div>
              <div class="notif-type__desc">
                New transactions and card-to-card transfers, incoming money requests, and emoji
                reactions appear instantly in your feed via a live connection — no setup required.
              </div>
            </div>
          </div>
        </section>

        <section v-if="activeSection === 'privacy'">
          <div class="settings-section__header">
            <h2 class="settings-section__title">Privacy & Data</h2>
          </div>
          <div class="privacy-info">
            <div class="info-box">
              Your financial data is encrypted and stored securely. Family Wallet processes your
              Monobank transactions only within your family group. See our
              <a href="/privacy.pdf" target="_blank" rel="noopener noreferrer" class="link"
                >Privacy Policy</a
              >
              for details.
            </div>
          </div>
        </section>
      </main>
    </div>

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
  import { fetchGroupCards, disconnectMonobankCard } from '../services/cardService'

  import ConnectCardModal from '../components/ConnectCardModal.vue'
  import ConfirmDialog from '../components/ConfirmDialog.vue'
  import NavBar from '../components/NavBar.vue'
  import { useRoute } from 'vue-router'
  import CardDetailsModal from '../components/CardDetailsModal.vue'

  const route = useRoute()
  const activeSection = ref(route.query.section || 'members')

  watch(
    () => route.query.section,
    (section) => {
      activeSection.value = section || 'members'
    },
    { immediate: true },
  )

  const { currentUser, isAdmin } = useAuth()

  const navItems = [
    { key: 'members', icon: '👥', label: 'Group Members' },
    { key: 'cards', icon: '💳', label: 'Connected Cards' },
    { key: 'notifications', icon: '🔔', label: 'Notifications' },
    { key: 'privacy', icon: '🛡', label: 'Privacy & Data' },
  ]

  const groupMembers = ref([])
  const isLoadingMembers = ref(false)

  function formatJoinedDate(isoDate) {
    if (!isoDate) return ''
    return new Date(isoDate).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    })
  }

  function mapMemberFromApi(apiMember, currentUserId) {
    const fullName = apiMember.name || 'User'
    const initials = fullName
      .split(' ')
      .map((w) => w[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)

    const variants = ['gold', 'dark', 'light']
    const variantIdx = (initials.charCodeAt(0) || 0) % variants.length

    return {
      id: apiMember.id,
      name: fullName,
      initials,
      role: apiMember.role || 'MEMBER',
      avatarVariant: variants[variantIdx],
      email: apiMember.email || '—',
      joinedAt: apiMember.joined_at ? formatJoinedDate(apiMember.joined_at) : '—',
      isCurrentUser: apiMember.id === currentUserId,
    }
  }

  async function loadGroupMembers() {
    const storedUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
    if (!storedUser.groupId) return

    isLoadingMembers.value = true
    try {
      const data = await fetchGroupMembers(storedUser.groupId)
      const members = Array.isArray(data) ? data : data.members || []
      groupMembers.value = members.map((m) => mapMemberFromApi(m, currentUser.value?.id))
    } catch {
      showToast('Failed to load group members', 'error')
    } finally {
      isLoadingMembers.value = false
    }
  }

  onMounted(() => {
    loadGroupMembers()
    loadCards()
  })

  function removeMember(member) {
    if (!confirm(`Remove ${member.name} from the group?`)) return
    showToast('Remove member endpoint not available yet', 'info')
  }

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

      inviteUrl.value = data.invite_link
      inviteExpiresAt.value = data.expires_at

      showToast(inviteUrl.value ? 'New link generated' : 'Invite link ready', 'success')
    } catch (err) {
      const status = err.response?.status
      if (status === 403) {
        showToast('Only Admin can generate invite links', 'error')
      } else {
        showToast(err.userMessage || 'Error generating invite link. Try again.', 'error')
      }
    } finally {
      isGeneratingLink.value = false
    }
  }

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

  async function sendDirectInvite() {
    if (!directEmail.value.trim()) return
    isSendingDirectInvite.value = true
    try {
      showToast(`Invite sent to ${directEmail.value}`, 'success')
      directEmail.value = ''
    } catch {
      showToast('Failed to send invite. Try again.', 'error')
    } finally {
      isSendingDirectInvite.value = false
    }
  }

  const connectedCards = ref([])
  const isLoadingCards = ref(false)
  const isConnectCardOpen = ref(false)

  const isConfirmOpen = ref(false)
  const isCardDetailsOpen = ref(false)
  const selectedCardForDetails = ref(null)

  function openCardDetails(card) {
    selectedCardForDetails.value = card
    isCardDetailsOpen.value = true
  }

  function closeCardDetails() {
    isCardDetailsOpen.value = false
    selectedCardForDetails.value = null
  }

  const cardToDisconnect = ref(null)
  const isDisconnecting = ref(false)

  function isOwnCard(card) {
    return String(card.user_id) === String(currentUser.value?.id)
  }

  async function loadCards() {
    if (!currentUser.value?.groupId) return
    isLoadingCards.value = true
    try {
      connectedCards.value = await fetchGroupCards(currentUser.value.groupId)
    } catch {
      showToast('Failed to load connected cards', 'error')
    } finally {
      isLoadingCards.value = false
    }
  }

  async function handleCardConnected() {
    await loadCards()
  }

  function askDisconnect(card) {
    cardToDisconnect.value = card
    isConfirmOpen.value = true
  }

  async function confirmDisconnect() {
    if (!cardToDisconnect.value) return

    const card = cardToDisconnect.value
    isDisconnecting.value = true

    try {
      await disconnectMonobankCard(card.id)

      connectedCards.value = connectedCards.value.filter((c) => c.id !== card.id)

      showToast('Card disconnected successfully. Transaction history is preserved.', 'success')
      isConfirmOpen.value = false
      cardToDisconnect.value = null
    } catch (err) {
      const status = err.response?.status
      const message = err.response?.data?.detail || err.response?.data?.message

      if (status === 403) {
        showToast(message || 'You can only disconnect your own cards', 'error')
      } else if (status === 404) {
        // Картка вже видалена — синхронізуємо UI
        connectedCards.value = connectedCards.value.filter((c) => c.id !== card.id)
        showToast('Card was already disconnected', 'info')
        isConfirmOpen.value = false
        cardToDisconnect.value = null
      } else {
        showToast(err.userMessage || 'Failed to disconnect card', 'error')
      }
    } finally {
      isDisconnecting.value = false
    }
  }

  function cancelDisconnect() {
    isConfirmOpen.value = false
    cardToDisconnect.value = null
  }

  const toast = ref({ isVisible: false, message: '', type: 'success' })

  /**
   * @param {string} message
   * @param {'success'|'error'|'info'} type
   */
  function showToast(message, type = 'success') {
    toast.value = { isVisible: true, message, type }
    setTimeout(() => {
      toast.value.isVisible = false
    }, 3000)
  }
</script>

<style scoped>
  .settings-page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: #faf8f3;
  }

  .settings-layout {
    display: flex;
    flex: 1;
    height: calc(100vh - 60px);
    overflow: hidden;
  }

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

  .invite-ttl {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    color: #9b7a25;
    margin-bottom: 16px;
  }

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

  .notif-type {
    margin-top: 14px;
  }
  .notif-type__title {
    font-size: 13px;
    font-weight: 600;
    color: #0d0c0a;
    margin-bottom: 4px;
  }
  .notif-type__desc {
    font-size: 13px;
    color: #6b6860;
    line-height: 1.6;
  }

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

  .cards-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    padding: 48px 20px;
    background: #ffffff;
    border: 1px dashed #d6d3ce;
    border-radius: 12px;
    text-align: center;
  }

  .cards-empty p {
    font-size: 14px;
    font-weight: 600;
    color: #0d0c0a;
    margin: 8px 0 0;
  }

  .cards-empty span {
    font-size: 12px;
    color: #b0ada7;
  }

  .card-item {
    display: flex;
    gap: 14px;
    align-items: center;
    padding: 16px 20px;
    background: linear-gradient(135deg, #faf8f3, #fbf7ec);
    border: 1px solid #f2e9c8;
    border-radius: 12px;
    margin-bottom: 10px;
  }

  .card-item__icon {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    background: linear-gradient(135deg, #fbf7ec, #f4f1e9);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .card-item__info {
    flex: 1;
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
  }

  .card-item__owner {
    font-size: 12px;
    color: #6b6860;
    margin-top: 4px;
    letter-spacing: 0.2px;
  }

  .cards-loading {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .card-skeleton {
    height: 76px;
    background: linear-gradient(90deg, #ede9de 25%, #f4f1e9 50%, #ede9de 75%);
    background-size: 200% 100%;
    animation: shimmer 1.6s ease infinite;
    border-radius: 12px;
  }

  .btn-details {
    padding: 6px 14px;
    background: #ffffff;
    color: #9b7a25;
    border: 1.5px solid #dfc876;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
    font-family: 'DM Sans', system-ui, sans-serif;
  }

  .btn-details:hover {
    background: #fbf7ec;
    border-color: #b8973a;
  }

  @keyframes shimmer {
    0% {
      background-position: 200% 0;
    }
    100% {
      background-position: -200% 0;
    }
  }

  @media (max-width: 768px) {
    .settings-layout {
      flex-direction: column;
      height: auto;
    }
    .settings-nav {
      width: 100%;
      display: flex;
      overflow-x: auto;
      padding: 8px 12px;
      border-right: none;
      border-bottom: 1px solid #eae8e4;
      -webkit-overflow-scrolling: touch;
      flex-shrink: 0;
    }
    .settings-nav::-webkit-scrollbar {
      display: none;
    }
    .settings-nav__item {
      flex-shrink: 0;
      border-left: none;
      border-bottom: 3px solid transparent;
      padding: 10px 16px;
      white-space: nowrap;
      width: auto;
    }
    .settings-nav__item--active {
      border-left-color: transparent;
      border-bottom-color: #b8973a;
    }
    .settings-main {
      padding: 24px 16px;
    }

    .members-table-wrap {
      background: transparent;
      border: none;
      box-shadow: none;
    }
    .members-table thead {
      display: none;
    }
    .members-table,
    .members-table tbody,
    .members-table tr,
    .members-table td {
      display: block;
      width: 100%;
    }
    .members-table tr {
      background: #ffffff;
      border: 1px solid #eae8e4;
      border-radius: 12px;
      margin-bottom: 10px;
      padding: 12px;
    }
    .members-table td {
      padding: 6px 0;
      border-bottom: none;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .members-table td::before {
      content: attr(data-label);
      font-size: 10px;
      font-weight: 700;
      color: #b0ada7;
      letter-spacing: 0.8px;
      text-transform: uppercase;
    }

    .invite-section {
      padding: 20px 16px;
    }
    .invite-link-box {
      flex-direction: column;
    }
    .invite-link-box__url {
      border-right: none;
      border-bottom: 1px solid #f2e9c8;
      font-size: 11px;
      padding: 10px 12px;
    }
    .btn-copy {
      width: 100%;
      padding: 12px;
      justify-content: center;
    }
    .invite-direct__row {
      flex-direction: column;
    }

    .card-item {
      flex-wrap: wrap;
      gap: 10px;
    }
    .card-item__actions {
      width: 100%;
      justify-content: flex-end;
    }
  }

  @media (max-width: 480px) {
    .settings-section__title {
      font-size: 20px;
    }
    .settings-main {
      padding: 20px 12px;
    }
  }
</style>
