<template>
  <v-list-tile v-if="serviceWorkerRegistered()" @click>
    <v-list-tile-action>
      <v-checkbox :value="notificationEnabled()"></v-checkbox>
    </v-list-tile-action>

    <v-list-tile-content @click="togglePermission()">
      <v-list-tile-title>Notifications</v-list-tile-title>
      <v-list-tile-sub-title>Allow push notifications</v-list-tile-sub-title>
    </v-list-tile-content>
  </v-list-tile>

  <!--div >
    <p>Notfications</p>
    <v-btn icon :color="notificationEnabled()?'success':'normal'" >
      <v-icon>{{notificationEnabled()?'notifications':'notifications_off'}}</v-icon>
    </v-btn>
  </div-->
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
