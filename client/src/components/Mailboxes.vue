<template>
  <div class="webmail">
    <md-list class="mailboxes">
      <md-subheader>Mailboxes <md-button class="md-icon-button" @click="refreshMailboxes()"><md-icon>refresh</md-icon></md-button></md-subheader>
      <md-list-item v-for="mailbox in allMailboxes()" :key="mailbox.uid">

        <router-link :to="{name: 'mailbox', params: { id: mailbox.uid }}">
          <md-avatar>
            <img :src="gravatarUrl(mailbox)" alt="People">
          </md-avatar>
          <div class="md-list-text-container">
            <span v-if="mailbox.name">{{mailbox.name}}</span>
            <span v-if="!mailbox.name">{{mailbox.address}}</span>
            <span>{{mailbox.last_message.fromNow()}} - {{mailbox.messages.length}} msgs</span>
          </div>
          <md-button v-if="mailbox.unreads" class="md-icon-button md-list-action">
            <md-icon class="md-primary">chat_bubble</md-icon>
            <span v-if="mailbox.unreads <= 9" class="unread-count">{{mailbox.unreads}}</span>
            <span v-if="mailbox.unreads > 9" class="unread-count">9+</span>
          </md-button>
          <md-divider class="md-inset"></md-divider>
        </router-link>

      </md-list-item>
    </md-list>
    <div class="filler" v-if="$route.name === 'mailboxes'">Select a mailbox from left...</div>
    <router-view></router-view>
  </div>
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
      if (this.allMailboxes() === null) {
        this.refreshMailboxes()
      }
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

.webmail{
  flex: 1;
  display: flex;
  overflow: hidden;
  &.loading {
    display: none;
  }
}

.mailboxes{
  flex: 2;
  overflow-y: scroll;
  background-color: #DBE2E5;
}

.filler{
  flex: 8;
}

.unread-count{
  position: absolute;
  top: 7px;
  left: 8px;
  color: white;
  text-align: center;
  width: 2em;
  font-size: 0.9em;
}

</style>
