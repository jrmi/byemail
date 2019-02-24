<template>
  <v-card v-if="currentMailbox()">
    <v-toolbar color="grey" dark flat>
      <v-toolbar-title>Mailbox: {{currentMailbox().name}} &lt;{{currentMailbox().address}}&gt;</v-toolbar-title>

      <v-spacer></v-spacer>

      <v-btn icon @click="writeMail()">
        <v-icon>email</v-icon>
      </v-btn>
      <v-btn icon v-if="currentMailbox().unreads" @click="markAllMailRead">
        <v-icon>visibility_off</v-icon>
      </v-btn>
    </v-toolbar>

    <message-list :messages="currentMailbox().messages" :userId="$route.params.userId"/>
  </v-card>
</template>

<script>
import { mapGetters, mapActions, mapMutations } from "vuex";
import _ from "lodash";
import MessageList from "@/components/MessageList";

export default {
  name: "mailbox",
  created() {
    this.fetchData();
  },
  watch: {
    // call again the method if the route changes
    $route: "fetchData"
  },
  methods: {
    fetchData() {
      this.setLoading(true);
      const mailboxId = this.$route.params.mailboxId;
      const userId = this.$route.params.userId;
      this.getMailbox({
        mailboxId,
        userId
      }).then(() => {
        this.setLoading(false);
      });
    },
    writeMail() {
      this.resetDraft();
      const newRecipient = {
        id: _.uniqueId(),
        address: this.currentMailbox().address,
        type: "to"
      };
      this.addDraftRecipient({ recipient: newRecipient });
      this.$router.push({ name: "mailedit" });
    },
    ...mapGetters(["currentMailbox"]),
    ...mapActions(["markAllMailRead", "setLoading", "getMailbox"]),
    ...mapMutations(["resetDraft", "addDraftRecipient"])
  },
  components: {
    MessageList
  },
  data() {
    return {
      error: null
    };
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
</style>
