<template>
  <v-card v-if="currentMail() && showMail">
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
      <span v-for="to of currentMail().recipients" :key="to.addr_spec">To: {{to.addr_spec}}</span>
    </div>

    <message-content :message="currentMail()" />

    <div class="mail-actions" v-if="showCompose">
      <quick-reply :mailbox="currentMailbox()" :message="currentMail()" @reply="reply" />
    </div>

  </v-card>
</template>

<script>
// import Moment from 'moment'
import { mapGetters, mapActions } from 'vuex'
import MessageContent from '@/components/MessageContent'
import QuickReply from '@/components/QuickReply'

export default {
  name: 'mail',
  created () {
    this.fetchData()
  },
  watch: {
    // call again the method if the route changes
    '$route': 'fetchData'
  },
  methods: {
    fetchData () {
      this.showMail = true
      this.setLoading(true)
      let mailId = this.$route.params.mail_id
      this.$store.dispatch({ type: 'getMail', mailId }).then(() => {
        this.setLoading(false)
      })
    },
    reply (data) {
      this.setLoading(true)
      this.sendMail(data).then((response) => {
        this.showCompose = false
        this.setLoading(false)
      })
    },
    ...mapGetters([
      'currentMail',
      'currentMailbox'
    ]),
    ...mapActions([
      'markMailRead',
      'sendMail',
      'setLoading'
    ])
  },
  components: {
    MessageContent,
    QuickReply
  },
  data () {
    return {
      showCompose: false,
      showMail: true,
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.mail {
  flex: 70;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.mail-header{
  flex: 0;
  overflow-y: scroll;
  min-height: 1.5em;
  border-bottom: 1px solid #ccc;
}
</style>
