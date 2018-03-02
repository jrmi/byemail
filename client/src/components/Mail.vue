<template>
  <div class="mail" v-if="currentMail() && showMail">
    <md-toolbar class="md-dense md-warn">
      <h2 class="md-title">{{currentMail().subject}} ({{currentMail()['body-type']}})</h2>
      <md-button @click="showCompose = ! showCompose" class="md-icon-button">
        <md-icon>reply</md-icon>
      </md-button>
      <md-button @click="showMail = ! showMail" class="md-icon-button">
        <md-icon>close</md-icon>
      </md-button>
      <md-button v-if="currentMail().unread" @click="markMailRead()" class="md-icon-button">
        <md-icon>visibility</md-icon>
      </md-button>
    </md-toolbar>

    <div class="mail-header">
      <span v-for="to of currentMail().recipients" :key="to.addr_spec">To: {{to.addr_spec}}</span>
    </div>

    <div class="mail-content">
      <p class="text" v-if="currentMail()['body-type'] == 'text/plain'" v-html="currentMail().body"></p>
      <iframe class="html" v-if="currentMail()['body-type'] == 'text/html'" :src="currentMail().iframeSrc">
        {{currentMail().body}}
      </iframe>
      <div class="mail-attachments" v-if="currentMail().attachments">
        <h3>{{currentMail().attachments.length}} <md-icon>attachment</md-icon></h3>
        <ul v-for="att of currentMail().attachments" :key="att.filename">
          <li><a :href="att.url">{{att.filename}}</a></li>
        </ul>
      </div>
    </div>

    <div class="mail-actions">
      <div class="mail-compose" v-if="showCompose">
        <textarea v-model="composeContent"></textarea>
        <md-button @click="reply()"><md-icon>send</md-icon></md-button>
      </div>

    </div>

  </div>
</template>

<script>
// import Moment from 'moment'
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'mail',
  created () {
    this.fetchData()
  },
  watch: {
    // call again the method if the route changes
    '$route': 'fetchData'
  },
  methods: {
    fetchData () {
      this.showMail = true
      this.setLoading(true)
      let mailId = this.$route.params.mail_id
      this.$store.dispatch({ type: 'getMail', mailId }).then(() => {
        this.setLoading(false)
      })
    },
    reply () {
      let data = {
        subject: 'Re: ' + this.currentMail().subject,
        reply_to: this.currentMail().id,
        recipients: [
          {
            address: this.currentMailbox().name + ' <' + this.currentMailbox().address + '>',
            type: 'to'
          }
        ],
        content: this.composeContent
      }
      this.setLoading(true)
      this.sendMail(data).then(function (response) {
        this.showCompose = false
        this.composeContent = ''
        this.setLoading(false)
      })
    },
    ...mapGetters([
      'currentMail',
      'currentMailbox'
    ]),
    ...mapActions([
      'markMailRead',
      'sendMail',
      'setLoading'
    ])
  },
  data () {
    return {
      showCompose: false,
      showMail: true,
      composeContent: ''
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.mail {
  flex: 70;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.md-toolbar{
  .md-title{
    flex: 1;
  }
}
.mail-attachments{
  background-color: #258097;
  color: #eee;
  padding-left: 10px;
  flex: 0;
  max-width: 30%;
  //overflow-x: scroll;
  ul {
    margin: 0 5px;
    padding: 0;
  }
  li {
    list-style-type: none;
    overflow: hidden;
    white-space:nowrap;
    text-overflow: ellipsis;
  }
}
.mail-header{
  flex: 0;
  overflow-y: scroll;
  min-height: 1.5em;
  border-bottom: 1px solid #ccc;
}
.mail-content{
  border: none;
  flex: 9;
  overflow-y: hidden;
  display: flex;
  .text, .html{
    flex: 1;
    overflow-y: scroll;
    padding: 5px;
    border: none;
  }
}
.mail-actions{
  background-color: #258097;
  color: #eee;
  padding: 5px;
}
.mail-compose{
  display: flex;
  flex-flow: row;
  textarea{
    font-size: 1.2em;
    width: 100%;
    min-height: 100px;
    margin: 5px;
  }
}
</style>
