<template>
  <v-card>
    <message-composer @sendMessage="send" :userId="$route.params.userId"/>
    <div class="actions">
      <v-btn @click="goBack()">Cancel</v-btn>
    </div>
  </v-card>
</template>

<script>
import { mapActions } from 'vuex'
import MessageComposer from '@/components/MessageComposer'

export default {
  name: 'mailedit',
  data() {
    return {}
  },
  components: {
    MessageComposer
  },
  methods: {
    goBack() {
      // TODO verify dirtyness
      this.$router.go(-1)
    },
    send(data) {
      this.setLoading(true)
      this.sendMail(data).then(response => {
        this.setLoading(false)
        this.$router.go(-1)
      })
    },
    ...mapActions(['sendMail', 'setLoading'])
  }
}
</script>

<style scoped lang="less">
</style>
