<template>
  <v-card>
    <message-composer/>
  </v-card>
</template>

<script>
import _ from 'lodash'
import { mapActions } from 'vuex'
import MessageComposer from '@/components/MessageComposer'

export default {
  name: 'mailedit',
  data () {
    return {
    }
  },
  components: {
    MessageComposer
  },
  methods: {
    goBack () {
      // TODO verify dirtyness
      this.$router.go(-1)
    },
    send () {
      this.setLoading(true)
      this.prepareAttachment().then((attachments) => {
        let data = {
          recipients: this.recipients,
          attachments: attachments,
          subject: this.mailSubject,
          content: this.mailContent
        }
        this.sendMail(data).then(response => {
          this.setLoading(false)
          this.$router.go(-1)
        })
      })
    },
    ...mapActions([
      'sendMail',
      'setLoading'
    ])
  }

}
</script>

<style scoped lang="less">


</style>
