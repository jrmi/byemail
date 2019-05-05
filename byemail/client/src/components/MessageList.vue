<template>
  <v-list two-line class="maillist">
    <template v-for="message in messages">
      <v-list-tile
        :key="message.uid"
        avatar
        :to="{ name: 'mail', params: {mailId: message.uid, userId}}"
        :class="{'incoming': message.incoming}"
      >
        <v-list-tile-content>
          <v-list-tile-title v-if="message.subject">{{message.subject}}</v-list-tile-title>
          <v-list-tile-title v-else>(No subject)</v-list-tile-title>
          <v-list-tile-sub-title>
            <span>{{message.date.fromNow()}}</span>
            <span v-if="message.attachments.length">
              | {{message.attachments.length}}
              <v-icon>attach_file</v-icon>
            </span>
          </v-list-tile-sub-title>
        </v-list-tile-content>

        <v-list-tile-action v-if="unreads && unreads[message.uid]">
          <v-icon color="grey lighten-1">visibility</v-icon>
        </v-list-tile-action>
      </v-list-tile>
    </template>
  </v-list>
</template>

<script>
export default {
  name: 'message-list',
  props: ['messages', 'unreads', 'userId']
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.maillist {
  .incoming {
    background-color: #d2e4db;
  }
}
</style>
