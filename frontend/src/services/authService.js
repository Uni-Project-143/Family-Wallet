import apiClient from './apiClient'
import { scheduleAfterJoin } from '../utils/cardReminder'

export async function registerUser(payload) {
  const response = await apiClient.post('/api/v1/auth/register', {
    fullName: payload.fullName,
    email: payload.email,
    password: payload.password,
    confirmPassword: payload.confirmPassword,
  })
  return response.data
}

/**
 * @returns {{ access_token: string, token_type: string }}
 */
export async function loginUser(credentials) {
  const response = await apiClient.post('/api/v1/auth/login', {
    email: credentials.email,
    password: credentials.password,
  })
  return response.data
}

/**
 * @returns {Promise<Array<{id: string, name: string, role: 'ADMIN'|'MEMBER'}>>}
 */
export async function fetchMyGroups() {
  const response = await apiClient.get('/api/v1/group/me')
  return response.data
}

export async function fetchGroupInviteLink(groupId) {
  const response = await apiClient.get(`/api/v1/group/${groupId}/invite`)
  return response.data
}

export async function regenerateGroupInviteLink(groupId) {
  const response = await apiClient.post(`/api/v1/group/${groupId}/invite/regenerate`)
  return response.data
}

export async function createGroup(name) {
  const response = await apiClient.post('/api/v1/group/', { name })
  scheduleAfterJoin()
  return response.data
}

export async function joinGroup(inviteLink) {
  const response = await apiClient.post('/api/v1/group/join', {
    invite_link: inviteLink,
  })
  scheduleAfterJoin()
  return response.data
}
/**
 * @param {{ email: string }} payload
 * @returns {{ message: string }}
 */
export async function requestPasswordReset(payload) {
  const response = await apiClient.post('/api/v1/auth/forgot-password', {
    email: payload.email,
  })
  return response.data
}

/**
 * @param {{ token: string, new_password: string }} payload
 * @returns {{ message: string }}
 */
export async function resetPassword(payload) {
  const response = await apiClient.post('/api/v1/auth/reset-password', {
    token: payload.token,
    new_password: payload.new_password,
  })
  return response.data
}
export async function fetchGroupMembers(groupId) {
  try {
    const response = await apiClient.get(`/api/v1/group/${groupId}/members`)
    return response.data
  } catch (err) {
    if (err.response?.status === 404) {
      return []
    }
    throw err
  }
}
/**
 * @returns {Promise<{ message: string }>}
 */
export async function logoutUser() {
  const response = await apiClient.post('/api/v1/auth/logout')
  return response.data
}
