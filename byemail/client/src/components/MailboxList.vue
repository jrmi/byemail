<template>
  <v-list class="blist" two-line>
    <template v-for="(mailbox, index) in mailboxes">
      <v-list-tile
        :key="mailbox.uid"
        avatar
        :to="{name: 'mailbox', params: { mailboxId: mailbox.uid, userId: userId }}"
      >
        <!-- v-list-tile-avatar>
          <img :src="gravatarUrl(mailbox)">
        </v-list-tile-avatar-->
        <v-list-tile-content>
          <v-list-tile-title v-if="mailbox.name" v-html="mailbox.name"></v-list-tile-title>
          <v-list-tile-title v-else v-html="mailbox.address"></v-list-tile-title>
          <v-list-tile-sub-title>{{mailbox.last_message.fromNow()}} - {{mailbox.total}} msgs</v-list-tile-sub-title>
        </v-list-tile-content>

        <v-list-tile-action
          v-if="unreads && unreads[mailbox.uid]&& Object.keys(unreads[mailbox.uid]).length"
        >
          <v-badge right overlap>
            <span
              slot="badge"
              v-if="Object.keys(unreads[mailbox.uid]).length <= 9"
            >{{Object.keys(unreads[mailbox.uid]).length}}</span>
            <span slot="badge" v-else>9+</span>
            <v-icon color="grey lighten-1">chat_bubble</v-icon>
          </v-badge>
        </v-list-tile-action>
      </v-list-tile>

      <v-divider v-if="index + 1 < mailboxes.length" :key="`divider-${index}`"></v-divider>
    </template>
  </v-list>
</template>

<script>
import md5 from 'crypto-js/md5'

export default {
  name: 'mailbox-list',
  props: ['mailboxes', 'unreads', 'userId'],
  created() {},
  methods: {
    gravatarUrl(mailbox) {
      let email = mailbox.address
      let hash = md5(email)
      return 'https://www.gravatar.com/avatar/' + hash + '?d=identicon'
    }
  },
  data() {
    return {}
  }
}
</script>

<style scoped lang="less">
</style>
