<template>
  <div v-if="!loading" class="webmail">
    <md-list class="mailboxes">
      <md-subheader>Mailboxes</md-subheader>
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
</template>

<script>
import { mapGetters } from 'vuex'
import md5 from 'crypto-js/md5'

export default {
  name: 'mailboxes',
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      this.loading = true
      this.$store.dispatch('getAllMailboxes').then(() => {
        this.loading = false
      })
    },
    gravatarUrl (mailbox) {
      let email = mailbox.address
      let hash = md5(email)
      return 'https://www.gravatar.com/avatar/' + hash + '?d=identicon'
    },
    ...mapGetters([
      'allMailboxes'
    ])
  },
  data () {
    return {
      loading: false
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
}

.mailboxes{
  flex: 2;
  overflow-y: scroll;
  background-color: #DBE2E5;
}

.filler{
  flex: 8;
}

</style>
