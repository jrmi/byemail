<template>
  <v-list three-line class="maillist">
    <template v-for="message in messages" >
      <!--v-subheader
        v-if="message.header"
        :key="message.uid"
      >
        {{ message.header }}
      </v-subheader-->


      <v-list-tile
        :key="message.uid"
        avatar
        :to="{ name: 'mail', params: {mail_id: message.uid}}"
        :class="{'incoming': message.incoming}"
      >
        <v-list-tile-content>
          <v-list-tile-title>{{message.subject}}</v-list-tile-title>
          <v-list-tile-sub-title><span class='text--primary'>{{message.date.fromNow()}}</span>
            <span v-if="message.attachments.length">
              | {{message.attachments.length}} <md-icon>attachment</md-icon>
            </span>
          </v-list-tile-sub-title>
        </v-list-tile-content>

        <v-list-tile-action v-if="message.unread">
          <v-icon color="grey lighten-1">visibility</v-icon>
        </v-list-tile-action>
      </v-list-tile>


    </template>
  </v-list>
  <!--div class="mailbox">

    <md-toolbar class="md-dense md-warn" v-if="currentMailbox()">
      <md-button class="md-icon-button">
        <md-icon>menu</md-icon>
      </md-button>

      <h2 class="md-title" style="flex: 1">Mailbox: {{currentMailbox().name}} &lt;{{currentMailbox().address}}&gt;</h2>
      <md-button @click="writeMail()" class="md-icon-button">
        <md-icon>email</md-icon>
      </md-button>

      <md-button v-if="currentMailbox().unreads" @click="markAllMailRead()" class="md-icon-button">
        <md-icon>visibility_off</md-icon>
      </md-button>
    </md-toolbar>

    <div class="maillist" v-if="currentMailbox()">
      <ul>
        <li v-for="message in currentMailbox().messages" :key="message.uid" :class="{'incoming': message.incoming}">
          <router-link :to="{ name: 'mail', params: {mail_id: message.uid}}">
            {{message.subject}} - {{message.date.fromNow()}}
          </router-link> 
          <span v-if="message.attachments.length">
            | {{message.attachments.length}} <md-icon>attachment</md-icon>
          </span>
          <span  v-if="message.unread">
            | <md-icon>visibility</md-icon>
          </span>
        </li>
      </ul>
    </div>

    <router-view></router-view>

  </div-->
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'message-list',
  props: ['messages'],
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.maillist{
  .incoming{
    background-color: #d2e4db;
  }
}
</style>
