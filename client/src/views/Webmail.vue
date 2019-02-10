<template>
  <div class="content" :class="{loading: isLoading()}" v-if="account">
    <v-toolbar app dense>
      <v-btn :to="{ name: 'mailboxes' }" icon>
        <v-icon>home</v-icon>
      </v-btn>
      <v-toolbar-title>Maiboxes for {{account.name}}</v-toolbar-title>
      <v-spacer></v-spacer>
      <notification-button/>
      <v-btn icon @click="logout()">
        <v-icon>input</v-icon>
      </v-btn>
    </v-toolbar>

    <v-content style="height: 100%">
      <router-view></router-view>
    </v-content>

    <v-footer :fixed="fixed" app>
      <span>Byemail for your pleasure &copy; 2018</span>
    </v-footer>

    <div class="waiter">
      <v-progress-circular :size="70" :width="7" color="purple" indeterminate class="centered"></v-progress-circular>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions, mapMutations } from "vuex";
import NotificationButton from "@/components/NotificationButton";

export default {
  name: "webmail",
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.setLoading(true);
      this.$http.get("/api/account").then(
        response => {
          this.account = response.body;
          this.setLoading(false);
        },
        response => {
          this.$router.push({ name: "login" });
          this.setLoading(false);
        }
      );
    },
    logout() {
      this.$http.get("/logout").then(response => {
        this.resetMailboxes();
        this.$router.push({ name: "login" });
      });
    },
    ...mapGetters(["isLoading"]),
    ...mapActions(["setLoading"]),
    ...mapMutations(["resetMailboxes"])
  },
  components: {
    NotificationButton
  },
  data() {
    return {
      clipped: false,
      drawer: false,
      fixed: false,
      items: [
        {
          icon: "all_inbox",
          title: "Home",
          route: { name: "mailboxes" }
        },
        {
          icon: "mail",
          title: "Compose message",
          route: { name: "mailedit" }
        },
        {
          icon: "input",
          title: "Log out",
          action: () => {
            this.logout();
          }
        }
      ],
      miniVariant: false,
      account: null
    };
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.content {
  height: 100%;

  .waiter {
    display: none;
    position: fixed;
    top: 0px;
    bottom: 0px;
    left: 0px;
    right: 0px;
    z-index: 10;
    background-color: rgba(0, 0, 0, 0.4);
  }

  &.loading .waiter {
    display: block;
  }
}

.centered {
  left: 50%;
  position: absolute;
  top: 50%;
  margin: -25px 0 0 -25px;
}
</style>
