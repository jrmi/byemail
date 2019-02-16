<template>
  <div>
    <span>{{notificationEnabled()?'Notification allowed':'Notification blolcked'}}</span>
    <v-btn
      :color="notificationEnabled()?'normal':'success'"
      :disabled="!serviceWorkerRegistered()"
      @click="togglePermission()"
    >{{notificationEnabled()?'Block':'Allow'}}</v-btn>
  </div>
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
