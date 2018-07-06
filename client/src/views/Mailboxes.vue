<template>
  <v-layout row>
    <v-flex xs4>
      <v-card _class="webmail">
        <v-toolbar color="grey" dark flat>

          <v-toolbar-title>Mailboxes</v-toolbar-title>

          <v-spacer></v-spacer>

          <v-btn icon @click="refreshMailboxes()">
            <v-icon>refresh</v-icon>
          </v-btn>

        </v-toolbar>
        <mailbox-list :mailboxes="allMailboxes()"/>
      </v-card>
    </v-flex>

    <v-flex xs8>
        <router-view></router-view>
        <div class="filler" v-if="$route.name === 'mailboxes'">Select a mailbox from left...</div>
    </v-flex>
  </v-layout>
</template>

<script>
import MailboxList from '@/components/MailboxList'
import { mapGetters, mapActions } from 'vuex'
import md5 from 'crypto-js/md5'

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
  },
  data () {
    return {
    }
  }
}
</script>

<style scoped lang="less">
.content{
  height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>
