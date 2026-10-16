export const THEME_KEY = 'aurapose_theme_mode'
export const PROFILE_KEY = 'aurapose_profile'

const themePalettes = {
  light: {
    mode: 'light',
    navFront: '#000000',
    navBg: '#f3f6fb',
    tabColor: '#7b8798',
    tabSelected: '#4c6fff',
    tabBg: '#f4f7fb',
    tabBorderStyle: 'white',
    pageBg: '#f3f6fb',
    pageBgSoft: '#ffffff',
    heroGlow: 'rgba(98, 129, 255, 0.18)',
    heroGlowAlt: 'rgba(114, 220, 205, 0.2)',
    surface: 'rgba(255, 255, 255, 0.84)',
    surfaceStrong: '#ffffff',
    surfaceSoft: '#edf2fb',
    surfaceTint: 'rgba(90, 116, 255, 0.08)',
    border: 'rgba(89, 103, 140, 0.12)',
    text: '#122033',
    textSecondary: '#5f6d82',
    textMuted: '#8591a4',
    brand: '#4c6fff',
    brandSoft: '#7690ff',
    accent: '#2dc5b4',
    accentSoft: '#e6fbf6',
    accentWarm: '#ff7f5c',
    overlay: 'rgba(10, 18, 35, 0.04)',
    shadow: '0 18rpx 56rpx rgba(76, 111, 255, 0.14)',
    badgeBg: 'rgba(18, 32, 51, 0.06)'
  },
  dark: {
    mode: 'dark',
    navFront: '#ffffff',
    navBg: '#0b1020',
    tabColor: '#6e7798',
    tabSelected: '#9cb3ff',
    tabBg: '#0d1325',
    tabBorderStyle: 'black',
    pageBg: '#0b1020',
    pageBgSoft: '#11182d',
    heroGlow: 'rgba(111, 134, 255, 0.28)',
    heroGlowAlt: 'rgba(52, 211, 191, 0.18)',
    surface: 'rgba(17, 24, 45, 0.82)',
    surfaceStrong: '#131b31',
    surfaceSoft: '#18213b',
    surfaceTint: 'rgba(156, 179, 255, 0.08)',
    border: 'rgba(151, 169, 214, 0.12)',
    text: '#f5f7ff',
    textSecondary: '#c2cadf',
    textMuted: '#7b87a8',
    brand: '#9cb3ff',
    brandSoft: '#b491ff',
    accent: '#7ce4d7',
    accentSoft: '#143d3f',
    accentWarm: '#ff9d7a',
    overlay: 'rgba(255, 255, 255, 0.04)',
    shadow: '0 22rpx 64rpx rgba(0, 0, 0, 0.28)',
    badgeBg: 'rgba(255, 255, 255, 0.06)'
  }
}

const sceneAssets = {
  strengthBuilder: {
    light: '/static/training/strength-builder-day.jpg',
    dark: '/static/training/strength-builder-night.jpg'
  },
  flowYoga: {
    light: '/static/training/flow-yoga-day.jpg',
    dark: '/static/training/flow-yoga-night.jpg'
  },
  coreBurst: {
    light: '/static/training/core-burst-day.jpg',
    dark: '/static/training/core-burst-night.jpg'
  },
  deepStretch: {
    light: '/static/training/deep-stretch-day.jpg',
    dark: '/static/training/deep-stretch-night.jpg'
  },
  hiitBurn: {
    light: '/static/training/hiit-burn-day.jpg',
    dark: '/static/training/hiit-burn-night.jpg'
  },
  bicepsCurl: {
    light: '/static/training/biceps-curl-day.jpg',
    dark: '/static/training/biceps-curl-night.jpg'
  },
  pullUp: {
    light: '/static/training/pull-up-day.jpg',
    dark: '/static/training/pull-up-night.jpg'
  },
  squat: {
    light: '/static/training/squat-day.jpg',
    dark: '/static/training/squat-night.jpg'
  }
}

export function normalizeThemeMode(mode) {
  return mode === 'light' ? 'light' : 'dark'
}

export function getThemeMode() {
  const stored = uni.getStorageSync(THEME_KEY)
  return normalizeThemeMode(stored)
}

export function setThemeMode(mode) {
  const normalized = normalizeThemeMode(mode)
  uni.setStorageSync(THEME_KEY, normalized)
  return normalized
}

export function getThemePalette(mode) {
  return themePalettes[normalizeThemeMode(mode)]
}

export function getThemeClass(mode) {
  return `theme-${normalizeThemeMode(mode)}`
}

export function getThemeVars(mode) {
  const palette = getThemePalette(mode)
  return {
    '--page-bg': palette.pageBg,
    '--page-bg-soft': palette.pageBgSoft,
    '--hero-glow': palette.heroGlow,
    '--hero-glow-alt': palette.heroGlowAlt,
    '--surface': palette.surface,
    '--surface-strong': palette.surfaceStrong,
    '--surface-soft': palette.surfaceSoft,
    '--surface-tint': palette.surfaceTint,
    '--border': palette.border,
    '--text': palette.text,
    '--text-secondary': palette.textSecondary,
    '--text-muted': palette.textMuted,
    '--brand': palette.brand,
    '--brand-soft': palette.brandSoft,
    '--accent': palette.accent,
    '--accent-soft': palette.accentSoft,
    '--accent-warm': palette.accentWarm,
    '--overlay': palette.overlay,
    '--shadow': palette.shadow,
    '--badge-bg': palette.badgeBg
  }
}

export function applyNativeTheme(mode) {
  const palette = getThemePalette(mode)
  const animation = { duration: 0, timingFunc: 'linear' }
  try {
    uni.setNavigationBarColor({
      frontColor: palette.navFront,
      backgroundColor: palette.navBg,
      animation
    })
  } catch (err) {
    console.warn('setNavigationBarColor failed', err)
  }

  try {
    uni.setTabBarStyle({
      color: palette.tabColor,
      selectedColor: palette.tabSelected,
      backgroundColor: palette.tabBg,
      borderStyle: palette.tabBorderStyle
    })
  } catch (err) {
    // Non-tab pages will throw here, which is expected.
  }
}

export function getSceneAsset(key, mode) {
  const assets = sceneAssets[key]
  if (!assets) {
    return '/static/logo.png'
  }
  const normalized = normalizeThemeMode(mode)
  return assets[normalized] || assets.dark
}

export function getStoredProfile() {
  return uni.getStorageSync(PROFILE_KEY) || {}
}

export function mergeStoredProfile(profile = {}) {
  const merged = {
    ...getStoredProfile(),
    ...profile
  }
  uni.setStorageSync(PROFILE_KEY, merged)
  return merged
}
