<template>
  <v-card class="whole-mail" v-if="currentMail() && showMail">
    <v-toolbar color="grey" dark flat>
      <v-toolbar-title>{{currentMail().subject}} ({{currentMail()['body-type']}})</v-toolbar-title>

      <v-spacer></v-spacer>

      <v-btn icon @click="showCompose = ! showCompose">
        <v-icon>reply</v-icon>
      </v-btn>
      <v-btn icon @click="showMail = ! showMail">
        <v-icon>close</v-icon>
      </v-btn>
      <v-btn icon v-if="currentMail().unread" @click="markMailRead()">
        <v-icon>visibility</v-icon>
      </v-btn>
    </v-toolbar>

    <div class="mail-header">
      <span class="to" v-for="mail of currentMail().recipients" :key="mail.addr_spec">
        To: {{mail.addr_spec}}
        <span
          v-if="!currentMail().incoming && currentMail().delivery_status[mail.addr_spec].status !== 'DELIVERED'"
        >
          <v-icon
            color="error"
            @click.stop="currentRecipient = {dest: mail, status: currentMail().delivery_status[mail.addr_spec]}; dialog = true"
          >error</v-icon>
        </span>
      </span>
      <span class="cc" v-for="mail of currentMail().carboncopy" :key="mail.addr_spec">
        | Cc: {{mail.addr_spec}}
        <span
          v-if="!currentMail().incoming && currentMail().delivery_status[mail.addr_spec].status !== 'DELIVERED'"
        >
          <v-icon
            color="error"
            @click.stop="currentRecipient = {dest: mail, status: currentMail().delivery_status[mail.addr_spec]}; dialog = true"
          >error</v-icon>
        </span>
      </span>
      <span>| Received {{currentMail().date.format('lll')}}</span>
    </div>

    <message-content :message="currentMail()"/>

    <div class="mail-actions" v-if="showCompose">
      <quick-reply :mailbox="currentMailbox()" :message="currentMail()" @reply="reply"/>
    </div>

    <v-dialog v-model="dialog" max-width="300">
      <v-card>
        <v-card-title class="headline">Delivery fails...</v-card-title>

        <v-card-text>
          Delivery failure for {{currentRecipient.dest.addr_spec}}.
          <br>Failure reason :
          <br>
          {{currentRecipient.status.reason}} : {{currentRecipient.status.smtp_info}}
          <br>
          <br>Do you want to resend it ?
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>

          <v-btn color="error darken-1" flat="flat" @click="dialog = false">Cancel</v-btn>

          <v-btn
            color="green darken-1"
            flat="flat"
            @click="dialog = false; resend(currentRecipient.dest.addr_spec)"
          >Resend</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
// import Moment from 'moment'
import { mapGetters, mapActions } from 'vuex'
import MessageContent from '@/components/MessageContent'
import QuickReply from '@/components/QuickReply'

export default {
  name: 'mail',
  created() {
    this.fetchData()
  },
  watch: {
    // call again the method if the route changes
    $route: 'fetchData'
  },
  methods: {
    fetchData() {
      this.showMail = true
      this.setLoading(true)
      let mailId = this.$route.params.mailId
      let userId = this.$route.params.userId
      this.getMail({ mailId, userId }).then(() => {
        this.setLoading(false)
      })
    },
    reply(data) {
      this.setLoading(true)
      this.sendMail(data).then(response => {
        this.showCompose = false
        this.setLoading(false)
      })
    },
    resend(to) {
      this.setLoading(true)
      this.resendMail({ to }).then(response => {
        this.setLoading(false)
      })
    },
    ...mapGetters(['currentMail', 'currentMailbox']),
    ...mapActions([
      'markMailRead',
      'sendMail',
      'resendMail',
      'setLoading',
      'getMail'
    ])
  },
  components: {
    MessageContent,
    QuickReply
  },
  data() {
    return {
      showCompose: false,
      showMail: true,
      dialog: false,
      currentRecipient: { dest: '', status: {} }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.whole-mail {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.mail .v-toolbar {
  flex: 0;
}
.mail-header {
  flex: 0;
  overflow-y: auto;
  min-height: 1.6em;
  border-bottom: 1px solid #ccc;
}
.mail-content {
  flex: 1;
  overflow-y: scroll;
}
</style>
