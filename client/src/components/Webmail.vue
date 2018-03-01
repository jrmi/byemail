<template>
  <div class="content"  :class="{loading: isLoading()}" v-if="account">
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

    <router-view></router-view>

    <div class="waiter"><div class="signal"></div></div>

  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'webmail',
  created () {
    this.fetchData()
  },
  methods: {
    fetchData () {
      this.setLoading(true)
      this.$http.get('/api/account').then(response => {
        this.account = response.body
        this.setLoading(false)
      }, response => {
        this.$router.push({ name: 'login' })
        this.setLoading(false)
      })
    },
    logout () {
      this.$http.get('/logout').then(response => {
        this.$router.push({ name: 'login' })
      })
    },
    ...mapGetters([
      'isLoading'
    ]),
    ...mapActions([
      'setLoading'
    ])
  },
  data () {
    return {
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

  .waiter{
    display: none;
    position: fixed;
    top: 0px;
    bottom: 0px;
    left: 0px;
    right: 0px;
    z-index: 10;
    background-color: rgba(0,0,0,0.4);
  }

  &.loading .waiter{
    display: block;
  }
}

.signal {
    border: 5px solid #333;
    border-radius: 30px;
    height: 50px;
    width: 50px;
    left: 50%;
    margin: -25px 0 0 -25px;
    opacity: 0;
    position: absolute;
    top: 50%;

    animation: pulsate 1s ease-out;
    animation-iteration-count: infinite;
}

@keyframes pulsate {
    0% {
      transform: scale(.1);
      opacity: 0.0;
    }
    50% {
      opacity: 1;
    }
    100% {
      transform: scale(1.2);
      opacity: 0;
    }
}

#topbar{
  flex: 0;
  .md-menu{
    float: right;
  }
}
</style>
