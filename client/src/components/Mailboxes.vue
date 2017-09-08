<template>
  <md-layout v-if="!loading" class="webmail row">
    <md-layout md-flex="30">
      <md-whiteframe md-tag="section">
        <md-list>
          <md-list-item v-for="mailbox in mailboxes" :key="mailbox.eid">
            <md-avatar>
              <img src="https://placeimg.com/40/40/people/1" alt="People">
            </md-avatar>
            <span><router-link :to="'/mailbox/' + mailbox.eid">
              {{mailbox.from}}
            </router-link></span>
          </md-list-item>
        </md-list>
      </md-whiteframe>
    </md-layout>
    <md-layout md-flex="70" v-if="currentMailbox">
      <md-layout md-column>
      <h2>Messages for {{currentMailbox.from}}</h2>
      <ul md-flex="90">
        <li v-for="message in currentMailbox.messages" :key="message.id">
          {{message.subject}}
        </li>
      </ul>
      </md-layout>
    </md-layout>
  </md-layout>
</template>

<script>
export default {
  name: 'bye',
  created () {
    this.fetchData()
  },
  watch: {
    // call again the method if the route changes
    '$route': 'fetchData'
  },
  methods: {
    fetchData () {
      let currentMailbox = this.$route.params.name || null
      this.loading = true
      if (currentMailbox) {
        this.$http.get('/api/mailbox/' + currentMailbox, {responseType: 'json'}).then(function (response) {
          this.loading = false
          this.currentMailbox = response.body
        })
      }
      this.$http.get('/api/mailboxes', {responseType: 'json'}).then(function (response) {
        this.loading = false
        this.mailboxes = response.body
      })
    },
    show () {
      console.log('cliked')
    }
  },
  mounted () {
    console.log('done')
  },
  data () {
    return {
      loading: false,
      mailboxes: null,
      error: null,
      currentMailbox: null
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
h1, h2 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: block;
  margin: 0 10px;
}

a {
  color: #42b983;
}
</style>
