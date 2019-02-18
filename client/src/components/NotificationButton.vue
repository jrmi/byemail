<template>
  <v-btn
    icon
    :color="notificationEnabled()?'success':'normal'"
    @click="togglePermission()"
    v-if="serviceWorkerRegistered()"
  >
    <v-icon>{{notificationEnabled()?'notifications':'notifications_off'}}</v-icon>
  </v-btn>
</template>

<script>
import { mapGetters, mapActions, mapMutations } from "vuex";

export default {
  name: "notification-button",
  props: ["account"],
  created() {
    this.checkNotificationStatus();
  },
  data() {
    return {};
  },
  methods: {
    togglePermission() {
      if (this.notificationEnabled()) {
        this.unsubscribeNotification();
      } else {
        this.subscribeNotification();
      }
    },
    ...mapGetters(["notificationEnabled", "serviceWorkerRegistered"]),
    ...mapActions([
      "checkNotificationStatus",
      "subscribeNotification",
      "unsubscribeNotification"
    ])
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
</style>
