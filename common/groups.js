export const GROUPS_KEY = 'aurapose_groups_state'

function buildDefaultState() {
  return {
    ownedGroups: [],
    joinedGroupIds: [],
    popularGroups: []
  }
}

function normalizeState(state = {}) {
  const base = buildDefaultState()
  return {
    ownedGroups: Array.isArray(state.ownedGroups) ? state.ownedGroups : base.ownedGroups,
    joinedGroupIds: Array.isArray(state.joinedGroupIds) ? state.joinedGroupIds : base.joinedGroupIds,
    popularGroups: Array.isArray(state.popularGroups) && state.popularGroups.length ? state.popularGroups : base.popularGroups
  }
}

export function getGroupState() {
  const stored = uni.getStorageSync(GROUPS_KEY)
  return normalizeState(stored)
}

export function saveGroupState(nextState) {
  const normalized = normalizeState(nextState)
  uni.setStorageSync(GROUPS_KEY, normalized)
  return normalized
}

export function createLocalGroup(payload = {}) {
  const state = getGroupState()
  const nextGroup = {
    id: `owned-${Date.now()}`,
    name: payload.name || '未命名群组',
    tag: payload.tag || '训练',
    members: 1,
    description: payload.description || '在这里发起你的训练陪伴计划。',
    coverTheme: payload.coverTheme || 'theme-sky',
    inviteCode: payload.inviteCode || `AP${String(Date.now()).slice(-6)}`
  }

  return saveGroupState({
    ...state,
    ownedGroups: [nextGroup, ...state.ownedGroups]
  })
}

export function joinLocalGroup(groupId) {
  const state = getGroupState()
  const joinedGroupIds = Array.from(new Set([...(state.joinedGroupIds || []), groupId]))
  const popularGroups = state.popularGroups.map((item) => (
    item.id === groupId
      ? { ...item, members: Number(item.members || 0) + 1 }
      : item
  ))

  return saveGroupState({
    ...state,
    joinedGroupIds,
    popularGroups
  })
}
