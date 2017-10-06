<template>
  <div class="content">
    <md-toolbar id="topbar">
        <h1 class="md-title">Leefmail for {{account.name}}</h1>
        <md-menu>
          <md-button md-menu-trigger>Menu</md-button>
          <md-menu-content>
            <md-menu-item @click="logout()">Log out</md-menu-item>
          </md-menu-content>
        </md-menu>
    </md-toolbar>

    <div v-if="!loading" class="webmail">
      <md-list class="mailboxes">
        <md-list-item v-for="mailbox in mailboxes" :key="mailbox.uid">

          <router-link :to="{name: 'mailbox', params: { id: mailbox.uid }}">
            <md-avatar>
              <img :src="gravatarUrl(mailbox)" alt="People">
            </md-avatar>
            <div class="md-list-text-container">
              <span v-if="mailbox.name">{{mailbox.name}}</span>
              <span v-if="!mailbox.name">{{mailbox.address}}</span>
              <span>{{mailbox.last_message.fromNow()}} - {{mailbox.messages.length}} msgs</span>
            </div>
            <md-button class="md-icon-button md-list-action">
              <md-icon :class="'md-primary'">chat_bubble</md-icon>
            </md-button>
            <md-divider class="md-inset"></md-divider>
          </router-link>

        </md-list-item>
      </md-list>
      <div class="filler" v-if="$route.name === 'mailboxes'">Select a mailbox from left...</div>
      <router-view></router-view>
    </div>

  </div>
</template>

<script>
import Moment from 'moment'
import md5 from 'crypto-js/md5'

export default {
  name: 'mailboxes',
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      this.loading = true
      this.$http.get('/api/account').then(response => {
        this.account = response.body
        this.$http.get('/api/mailboxes', {responseType: 'json'}).then(function (response) {
          this.loading = false
          this.mailboxes = response.body
          for (let mb of this.mailboxes) {
            mb.last_message = Moment(mb.last_message)
          }
        })
      })
    },
    gravatarUrl (mailbox) {
      let email = mailbox.address
      let hash = md5(email)
      return 'https://www.gravatar.com/avatar/' + hash + '?d=identicon'
    },
    logout () {
      this.$http.get('/logout').then(response => {
        this.$router.push({ name: 'login' })
      })
    }
  },
  data () {
    return {
      loading: false,
      mailboxes: null,
      account: null,
      error: null
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
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
}

.mailboxes{
  flex: 2;
  overflow-y: scroll;
  background-color: #DBE2E5;
}

.filler{
  flex: 8;
}

#topbar{
  flex: 0;
}
</style>
