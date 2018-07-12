<template>
  <div class="main">
    <div class="mailboxes">
      <v-card class="mailboxlist">
        <v-toolbar color="grey" dark flat>

          <v-toolbar-title>Mailboxes</v-toolbar-title>

          <v-spacer></v-spacer>

          <v-btn icon @click="refreshMailboxes()">
            <v-icon>refresh</v-icon>
          </v-btn>

        </v-toolbar>
        <mailbox-list :mailboxes="allMailboxes()"/>
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
import MailboxList from '@/components/MailboxList'
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'mailboxes',
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      this.refreshMailboxes()
    },
    refreshMailboxes () {
      this.setLoading(true)
      this.getAllMailboxes().then(() => {
        this.setLoading(false)
      })
    },
    ...mapGetters([
      'allMailboxes'
    ]),
    ...mapActions([
      'getAllMailboxes',
      'setLoading'
    ])
  },
  components: {
    MailboxList
  }
}
</script>

<style scoped lang="less">
.main{
  height: 100%;
  max-height: 100%;
  display: grid;
  grid-template-columns: 25% 30% auto;
}
.mailboxes{
  height: 100%;
  max-height: 100%;
  overflow-y: scroll;
}
.mailbox{
  height: 100%;
  max-height: 100%;
  overflow-y: scroll;
}
.mail{
  height: 100%;
  max-height: 100%;
  overflow-y: scroll;
}
</style>
