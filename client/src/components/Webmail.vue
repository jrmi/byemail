<template>
  <div class="content" v-if="account">
    <md-toolbar id="topbar">
        <md-menu>
          <md-button md-menu-trigger class="md-icon-button"><md-icon>menu</md-icon></md-button>
          <md-menu-content>
            <md-menu-item><router-link :to="{ name: 'mailedit'}">Compose message</router-link></md-menu-item>
            <md-menu-item @click="logout()">Log out</md-menu-item>
          </md-menu-content>
        </md-menu>
        <h1 class="md-title"><router-link :to="{ name: 'mailboxes'}">Maiboxes for {{account.name}}</router-link></h1>
    </md-toolbar>

    <router-view :account="account"></router-view>

  </div>
</template>

<script>

export default {
  name: 'webmail',
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      this.loading = true
      this.$http.get('/api/account').then(response => {
        this.account = response.body
        this.loading = false
      }, response => {
        this.$router.push({ name: 'login' })
        this.loading = false
      })
    },
    logout () {
      this.$http.get('/logout').then(response => {
        this.$router.push({ name: 'login' })
      })
    }
  },
  data () {
    return {
      loading: false,
      account: null
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.content{
  height: 100vh;
  display: flex;
  flex-direction: column;
}

#topbar{
  flex: 0;
  .md-menu{
    float: right;
  }
}
</style>
