<template>
  <div class="mail" v-if="currentMail">
    <div class="mail-title">
      <h2 md-title>{{currentMail.subject}} ({{currentMail['body-type']}})</h2>
    </div>
    <div class="mail-content">
      <p class="text" v-if="currentMail['body-type'] == 'text/plain'" v-html="currentMail.body"></p>
      <iframe class="html" v-if="currentMail['body-type'] == 'text/html'" :src="iframeSrc">
        {{currentMail.body}}
      </iframe>
      <div class="mail-attachments" v-if="currentMail.attachments.length">
        <h3>{{currentMail.attachments.length}} attachment(s)</h3>
        <ul v-for="att of currentMail.attachments" :key="att.filename">
          <li>{{att.filename}}</li>
        </ul>
      </div>
    </div>
    <div class="mail-actions">
      <md-button @click="showCompose = ! showCompose">Reply</md-button>
      <div class="mail-compose" v-if="showCompose">
        <textarea v-model="composeContent"></textarea>
        <md-button @click="reply()">Send</md-button>
      </div>
    </div>
  </div>
</template>

<script>
import Moment from 'moment'

var tagsToReplace = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;'
}

function sanitizeText (str) {
  return str.replace(/[&<>]/g, (tag) => { return tagsToReplace[tag] || tag })
}

export default {
  name: 'mail',
  props: {
    'currentMailbox': Object
  },
  created () {
    this.fetchData()
  },
  watch: {
    // call again the method if the route changes
    '$route': 'fetchData'
  },
  methods: {
    fetchData () {
      let currentMail = this.$route.params.mail_id
      if (!this.currentMail || this.currentMail.id !== currentMail) {
        this.currentMail = null

        this.loading = true
        this.$http.get('/api/mail/' + currentMail, { responseType: 'json' }).then(function (response) {
          this.loading = false
          this.currentMail = response.body
          this.currentMail.date = Moment(this.currentMail.date)
          if (this.currentMail['body-type'] === 'text/html') {
            this.iframeSrc = 'data:text/html;charset=' + this.currentMail['body-charset'] + ',' + escape(this.currentMail.body)
          } else {
            this.currentMail.body = sanitizeText(this.currentMail.body).replace(/\n/g, '<br />')
          }
        })
      }
    },
    reply () {
      let data = {
        subject: 'Re: ' + this.currentMail.subject,
        reply_to: this.currentMail.id,
        recipients: [
          {
            address: this.currentMailbox.name + ' <' + this.currentMailbox.address + '>',
            type: 'to'
          }
        ],
        content: this.composeContent
      }
      this.$http.post('/api/sendmail/', data).then(function (response) {
        this.showCompose = false
        this.composeContent = ''
      })
    }
  },
  data () {
    return {
      loading: false,
      error: null,
      currentMail: null,
      iframeSrc: null,
      showCompose: false,
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
.mail-title{
  background-color: #258097;
  color: #eee;
  padding-left: 10px;
}
.mail-attachments{
  background-color: #258097;
  color: #eee;
  padding-left: 10px;
  flex: 0;
  max-width: 30%;
  //overflow-x: scroll;
}
.mail-content{
  border: none;
  flex: 1;
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
