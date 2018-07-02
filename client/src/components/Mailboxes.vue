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
        <v-list class="mailboxes" two-line>
          <template v-for="(mailbox, index) in allMailboxes()">
            <v-subheader
              v-if="mailbox.header"
              :key="mailbox.uid"
            >
              {{ mailbox.header }}
            </v-subheader>

            <v-divider
              v-else-if="mailbox.divider"
              :inset="mailbox.inset"
              :key="mailbox.uid"
            ></v-divider>

            <v-list-tile
              v-else
              :key="mailbox.uid"
              avatar
              :to="{name: 'mailbox', params: { id: mailbox.uid }}"
            >
              <v-list-tile-avatar>
                <img :src="gravatarUrl(mailbox)">
              </v-list-tile-avatar>

              <v-list-tile-content>
                <v-list-tile-title v-if="mailbox.name" v-html="mailbox.name"></v-list-tile-title>
                <v-list-tile-title v-else v-html="mailbox.address"></v-list-tile-title>
                <v-list-tile-sub-title>{{mailbox.last_message.fromNow()}} - {{mailbox.messages.length}} msgs</v-list-tile-sub-title>
              </v-list-tile-content>


              <v-list-tile-action>
              <v-badge right overlap v-model="mailbox.unreads">
                <span slot="badge" v-if="mailbox.unreads <= 9">{{mailbox.unreads}}</span>
                <span slot="badge" v-else>9+</span>
                <v-icon color="grey lighten-1">
                  chat_bubble
                </v-icon>
              </v-badge>
              </v-list-tile-action>
            </v-list-tile>
          </template>
        </v-list>
      </v-card>
    </v-flex>

    <v-flex xs8>
        <router-view></router-view>
        <div class="filler" v-if="$route.name === 'mailboxes'">Select a mailbox from left...</div>
    </v-flex>
  </v-layout>
</template>

<script>
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
    gravatarUrl (mailbox) {
      let email = mailbox.address
      let hash = md5(email)
      return 'https://www.gravatar.com/avatar/' + hash + '?d=identicon'
    },
    ...mapGetters([
      'allMailboxes'
    ]),
    ...mapActions([
      'getAllMailboxes',
      'setLoading'
    ])
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

/*.webmail{
  flex: 1;
  display: flex;
  overflow: hidden;
  &.loading {
    display: none;
  }
}*/

.mailboxes{
  flex: 3;
  overflow-y: scroll;
  background-color: #DBE2E5;
}

.filler{
  flex: 8;
}

.unread-count{
  position: absolute;
  top: 2px;
  left: 0px;
  color: white;
  text-align: center;
  width: 2em;
  font-size: 0.9em;
}

</style>
