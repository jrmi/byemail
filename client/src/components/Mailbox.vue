<template>
  <v-card>      
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

    <v-list three-line class="maillist">
      <template v-for="message in currentMailbox().messages" >
        <v-subheader
          v-if="message.header"
          :key="message.uid"
        >
          {{ message.header }}
        </v-subheader>


        <v-list-tile
          v-else
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

        <v-divider
          :inset="message.inset"
          :key="message.uid"
        ></v-divider>

      </template>
    </v-list>

    <router-view></router-view>

</v-card>
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
  data () {
    return {
      error: null
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.mailbox{
  flex: 8;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #F4F4F4;
}
.md-toolbar{
  .md-title{
    flex: 1;
  }
}
.maillist{
  flex: 30;
  overflow-y: scroll;
  //border-bottom: 1px solid #ddd;
  ul{
    list-style-type: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
  }
  li{
    padding: 10px;
    margin: 2px;
    width: 100%;
    align-self: flex-end;
    background-color: #dad27e;
    border-radius: 2px;
  }
  .incoming{
    background-color: #d2e4db;
    align-self: flex-start;
  }
}
</style>
