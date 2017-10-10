<template>
  <div class="mailbox">
    <div class="mailbox-title" v-if="currentMailbox">
      <h2 md-title>Mailbox for: {{currentMailbox.name}} &lt;{{currentMailbox.address}}&gt;</h2>
    </div>
    <div class="maillist" v-if="currentMailbox">
      <ul>
        <li v-for="message in currentMailbox.messages" :key="message.uid" :class="{'incoming': message.incoming}">
          <router-link :to="{ name: 'mail', params: {mail_id: message.uid}}">
            {{message.subject}} - {{message.date.fromNow()}}
            <span v-if="message.attachment_count">
              - {{message.attachment_count}} attachments
            </span>
          </router-link>
        </li>
      </ul>
    </div>
    <router-view :current-mailbox="currentMailbox"></router-view>
  </div>
</template>

<script>
import Moment from 'moment'

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
      let currentMailbox = this.$route.params.id
      if (!this.currentMailbox || this.currentMailbox.uid !== currentMailbox) {
        this.currentMailbox = null
        this.loading = true
        this.$http.get('/api/mailbox/' + currentMailbox, {responseType: 'json'}).then(function (response) {
          this.loading = false
          this.currentMailbox = response.body
          for (let msg of this.currentMailbox.messages) {
            msg.date = Moment(msg.date)
          }
        })
      }
    }
  },
  data () {
    return {
      loading: false,
      error: null,
      currentMailbox: null
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
.mailbox-title{
  background-color: #258097;
  color: #eee;
  padding-left: 10px;
}
.maillist{
  flex: 30;
  overflow-y: scroll;
  border-bottom: 1px solid #ddd;
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
    width: 95%;
    align-self: flex-end;
    background-color: #dad27e;
    border-radius: 2px;
  }
  .incoming{
    background-color: #afe0c7;
    align-self: flex-start;
  }
}
</style>
