<template>
  <v-card v-if="currentMailbox()">      
    <v-toolbar color="grey" dark flat>

      <v-toolbar-title>Mailbox: {{currentMailbox().name}} &lt;{{currentMailbox().address}}&gt;</v-toolbar-title>

      <v-spacer></v-spacer>

      <v-btn icon @click="writeMail()">
        <v-icon>email</v-icon>
      </v-btn>
      <v-btn icon v-if="currentMailbox().unreads" @click="markAllMailRead()">
        <v-icon>visibility_off</v-icon>
      </v-btn>

    </v-toolbar>

    <message-list :messages="currentMailbox().messages" />
  </v-card>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import MessageList from "@/components/MessageList"

export default {
  name: 'mailbox',
  created () {
    this.fetchData()
  },
  watch: {
    // call again the method if the route changes
    '$route': 'fetchData'
  },
  methods: {
    fetchData () {
      this.setLoading(true)
      let mailboxId = this.$route.params.id
      this.$store.dispatch({ type: 'getMailbox', mailboxId }).then(() => {
        this.setLoading(false)
      })
    },
    writeMail () {
      this.$router.push({ name: 'mailedit' })
    },
    ...mapGetters([
      'currentMailbox'
    ]),
    ...mapActions([
      'markAllMailRead',
      'setLoading'
    ])
  },
  components: {
    MessageList
  },
  data () {
    return {
      error: null
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">

</style>
