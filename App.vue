<script>
import { applyTabBarLocale, getLocale } from './common/i18n.js'

export default {
  onLaunch() {
    applyTabBarLocale(getLocale())
  },
  onShow() {
    applyTabBarLocale(getLocale())
  },
  onHide() {}
}
</script>

<style>
/* global page styles */
</style>
