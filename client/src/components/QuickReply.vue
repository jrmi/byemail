<template>
  <div class="mail-compose" >
    <v-textarea v-model="composeContent"></v-textarea>
    <v-btn icon @click="reply()">
      <v-icon>send</v-icon>
    </v-btn>
  </div>
</template>

<script>
// import Moment from 'moment'
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'quick-reply',
  props: ['mailbox', 'message'],
  methods: {
    reply () {
      let data = {
        subject: 'Re: ' + this.message.subject,
        reply_to: this.message.id,
        recipients: [
          {
            address: this.mailbox.name + ' <' + this.mailbox.address + '>',
            type: 'to'
          }
        ],
        content: this.composeContent
      }
      this.$emit('reply', data)
      this.composeContent = ''
      /*this.setLoading(true)
      this.sendMail(data).then(function (response) {
        this.showCompose = false
        this.composeContent = ''
        this.setLoading(false)
      })*/
    },
  },
  data () {
    return {
      composeContent: ''
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
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
