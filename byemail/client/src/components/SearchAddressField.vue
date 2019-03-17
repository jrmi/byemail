<template>
  <v-layout>
    <v-flex xs2>
      <v-select v-model="type" :items="recipientTypes" @change="sendUpdate()"></v-select>
    </v-flex>
    <v-flex xs10>
      <v-combobox
        v-model="value"
        :items="entries"
        :loading="loading"
        :search-input.sync="search"
        item-text="name"
        item-value="name"
        @change="sendUpdate()"
      >Recipient</v-combobox>
    </v-flex>
  </v-layout>
</template>

<script>
import _ from 'lodash'

export default {
  name: 'message-composer',
  props: ['initValue', 'userId'],
  data() {
    return {
      recipientTypes: [
        { text: 'To', value: 'to' },
        { text: 'Cc', value: 'cc' },
        { text: 'Bcc', value: 'bcc' }
      ],
      type: 'to',
      entries: [],
      loading: false,
      search: '',
      value: ''
    }
  },
  created() {
    this.value = this.initValue
  },
  watch: {
    search(val) {
      val && this.querySelections(val)
    }
  },
  methods: {
    sendUpdate() {
      let name = this.value
      if (_.isObject(name)) {
        // FIXME Autocomplete bug workaround ?
        name = name.name
      }
      this.$emit('update', { type: this.type, address: name })
    },
    querySelections(val) {
      this.loading = true
      const userId = this.userId
      this.$http
        .get(`/api/users/${userId}/contacts/search`, {
          responseType: 'json',
          params: { text: val }
        })
        .then(function(response) {
          this.entries = response.body.map(item => {
            return { name: item }
          })
          this.loading = false
        })
    }
  }
}
</script>

<style scoped lang="less">
</style>
