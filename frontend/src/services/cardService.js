import apiClient from './apiClient'
import { scheduleAfterDisconnect } from '../utils/cardReminder'

export async function fetchMonobankCards(personalToken) {
  const response = await apiClient.post('/api/v1/monobank/client-info', {
    personal_token: personalToken,
  })
  return response.data
}

export async function connectMonobankCard(groupId, personalToken, card) {
  const response = await apiClient.post('/api/v1/monobank/connect', {
    group_id: groupId,
    personal_token: personalToken,
    account_id: card.account_id,
    masked_pan: card.masked_pan,
    balance: card.balance,
  })
  return response.data
}

/**
 * @param {string} cardId
 * @returns {Promise<{ message: string }>}
 */
export async function disconnectMonobankCard(cardId) {
  const response = await apiClient.delete(`/api/v1/monobank/card/${cardId}`)
  scheduleAfterDisconnect()
  return response.data
}

/**
 * @param {string} groupId
 * @returns {Promise<Array<{id, user_id, group_id, account_id, masked_pan, balance, effective_balance, virtual_balance, status, transaction_ids, owner_full_name}>>}
 */
export async function fetchGroupCards(groupId) {
  const response = await apiClient.get(`/api/v1/bank-cards/group/${groupId}`)
  return response.data
}
