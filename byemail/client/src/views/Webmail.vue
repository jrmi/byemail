<template>
  <div class="content" :class="{loading: isLoading()}" v-if="account()">
    <v-toolbar app dense>
      <v-btn icon @click="$router.back()" v-if="$route.name !== 'mailboxes'">
        <v-icon>arrow_back</v-icon>
      </v-btn>
      <v-toolbar-title>Account: {{account().address}}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon :to="{ name: 'settings', userId: $route.params.userId }">
        <v-icon>settings</v-icon>
      </v-btn>
      <v-btn icon @click="logout()">
        <v-icon>input</v-icon>
      </v-btn>
    </v-toolbar>

    <v-content>
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

export default {
  name: "webmail",
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.setLoading(true);
      this.loadAccount({ userId: this.$route.params.userId }).then(
        response => {
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
    ...mapGetters(["isLoading", "account"]),
    ...mapActions(["setLoading", "loadAccount"]),
    ...mapMutations(["resetMailboxes"])
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
      miniVariant: false
    };
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.content {
  height: 100%;
  //margin-top: 10px;
  //margin-bottom: -10px;

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
