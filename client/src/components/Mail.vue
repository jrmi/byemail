<template>
  <div class="mail" v-if="currentMail">
    <div class="mail-title">
      <h2 md-title>{{currentMail.subject}} ({{currentMail['body-type']}})</h2>
    </div>
    <p class="textMail" v-if="currentMail['body-type'] == 'text/plain'" v-html="currentMail.body"></p>
    <iframe class="htmlMail" v-if="currentMail['body-type'] == 'text/html'" :src="iframeSrc">
      {{currentMail.body}}
    </iframe>
    <div class="mail-attachments" v-if="currentMail.attachments">
      <span v-for="att of currentMail.attachments" :key="att.filename">
        {{att.filename}} |
      </span>
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
    }
  },
  data () {
    return {
      loading: false,
      error: null,
      currentMail: null,
      iframeSrc: null
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
}
.textMail{
  flex: 1;
  overflow-y: scroll;
  text-overflow: wrap;
  width: 100%;
}
.htmlMail{
  border: none;
  flex: 1;
  overflow-y: scroll;
}
</style>
