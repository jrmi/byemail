<template>
    <v-layout>
        <v-flex xs2>
            <v-select
            v-model="type"
            :items="recipientTypes"
            @change="sendUpdate()"
            ></v-select>
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
            >
                Recipient
            </v-combobox>
        </v-flex>
    </v-layout>
</template>

<script>

export default {
  name: 'message-composer',
  data () {
    return {
      recipientTypes: [
        {text: 'To', value: 'to'},
        {text: 'Cc', value: 'cc'},
        {text: 'Bcc', value: 'bcc'}
      ],
      type: 'to',
      value: '',
      entries: [],
      loading: false,
      search: ''
    }
  },
  watch: {
      search (val) {
          val && this.querySelections(val)
      }
  },
  methods: {
    sendUpdate () {
      this.$emit('update', {type: this.type, address: this.search})
    },
    querySelections (val) {
      this.loading = true
      this.$http.get('/api/contacts/search', { responseType: 'json', params: {text: val} }).then(function (response) {
        this.entries = response.body.map((item) => { return {name: item} })
        this.loading = false
      })
    }
  }

}
</script>

<style scoped lang="less">

</style>
