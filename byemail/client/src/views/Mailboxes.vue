<template>
  <div class="main" :class="`route_${$route.name}`">
    <div class="mailboxes">
      <v-card class="mailboxlist">
        <vue-pull-refresh :on-refresh="refreshMailboxes" :config="pull2RefreshConfig">
          <v-toolbar color="grey" dark flat>
            <v-toolbar-title>Mailboxes</v-toolbar-title>

            <v-spacer></v-spacer>

            <v-btn icon :to="{ name: 'mailedit' }">
              <v-icon>email</v-icon>
            </v-btn>

            <v-btn icon @click="refreshMailboxes()">
              <v-icon>refresh</v-icon>
            </v-btn>
          </v-toolbar>
          <mailbox-list :mailboxes="allMailboxes()" :userId="$route.params.userId"/>
        </vue-pull-refresh>
      </v-card>
    </div>
    <div class="mailbox">
      <div class="filler" v-if="$route.name === 'mailboxes'">Select a mailbox from left...</div>
      <router-view></router-view>
    </div>
    <div class="mail">
      <router-view name="mail"></router-view>
    </div>
  </div>
</template>

<script>
import MailboxList from "@/components/MailboxList";
import { mapGetters, mapActions } from "vuex";
import VuePullRefresh from "vue-pull-refresh";

export default {
  name: "mailboxes",
  data() {
    return {
      pull2RefreshConfig: {
        errorLabel: "Refresh failed !",
        startLabel: "Pull to refresh",
        readyLabel: "Release now",
        loadingLabel: "Loading...",
        pullDownHeight: "100"
      }
    };
  },
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.refreshMailboxes({ userId: this.$route.params.userId });
    },
    refreshMailboxes() {
      this.setLoading(true);
      this.getAllMailboxes({ userId: this.$route.params.userId }).then(
        () => {
          this.setLoading(false);
        },
        () => {
          console.log("Can't get mailboxes");
        }
      );
    },
    ...mapGetters(["allMailboxes", "account"]),
    ...mapActions(["getAllMailboxes", "setLoading"])
  },
  components: {
    MailboxList,
    "vue-pull-refresh": VuePullRefresh
  }
};
</script>

<style scoped lang="less">
.main {
  height: 89vh; // TODO find a better way
  max-height: 89vh;
  display: grid;
  grid-template-columns: 25% 30% auto;
}
.mailboxes {
  overflow-y: scroll;
}
.mailbox {
  overflow-y: scroll;
}
.mail {
  overflow-y: hidden;
  display: flex;
}

@media (max-width: 600px) {
  .main {
    grid-template-columns: 100%;
  }
  .mailboxes,
  .mailbox,
  .mail {
    display: none;
  }
  .route_mailboxes .mailboxes {
    display: block;
  }
  .route_mailbox .mailbox {
    display: block;
  }
  .route_mail .mail {
    display: block;
  }
}
@media (max-width: 960px) and (min-width: 600px) {
  .main {
    grid-template-columns: 40% auto;
  }
  .main.route_mail {
    grid-template-columns: 100%;
  }
  .mailboxes,
  .mailbox,
  .mail {
    display: none;
  }
  .route_mailboxes .mailboxes {
    display: block;
  }
  .route_mailboxes .mailbox {
    display: block;
  }
  .route_mailbox .mailboxes {
    display: block;
  }
  .route_mailbox .mailbox {
    display: block;
  }
  .route_mail .mail {
    display: block;
  }
}
</style>
