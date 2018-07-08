<template>
  <div class="content"  :class="{loading: isLoading()}" v-if="account">
    <v-navigation-drawer
      persistent
      :mini-variant="miniVariant"
      :clipped="clipped"
      v-model="drawer"
      enable-resize-watcher
      fixed
      app
    >
      <v-list>
        <div v-for="(item, i) in items" :key="i">

          <v-list-tile
            v-if="item.route"
            value="true"
            :to="item.route"
          >
            <v-list-tile-action>
              <v-icon>{{item.icon}}</v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
                <v-list-tile-title v-text="item.title">
                </v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>

          <v-list-tile
            v-if="item.action"
            value="true"
            :to="item.route"
            @click="item.action"
          >
            <v-list-tile-action>
              <v-icon>{{item.icon}}</v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title v-text="item.title" >
              </v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>

        </div>
      </v-list>
    </v-navigation-drawer>

    <v-toolbar
      app
      :clipped-left="clipped"
    >
      <v-toolbar-side-icon @click.stop="drawer = !drawer"></v-toolbar-side-icon>
      <v-toolbar-title>Maiboxes for {{account.name}}</v-toolbar-title>
      <v-spacer></v-spacer>
    </v-toolbar>

    <v-content style="height: 100%">
      <router-view></router-view>
    </v-content>

    <v-footer :fixed="fixed" app>
      <span>Byemail for your pleasure &copy; 2018</span>
    </v-footer>

    <div class="waiter"><div class="signal"></div></div>

  </div>
</template>

<script>
import { mapGetters, mapActions, mapMutations } from 'vuex'

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
        this.resetMailboxes()
        this.$router.push({ name: 'login' })
      })
    },
    ...mapGetters([
      'isLoading'
    ]),
    ...mapActions([
      'setLoading'
    ]),
    ...mapMutations([
      'resetMailboxes'
    ])
  },
  data () {
    return {
      clipped: false,
      drawer: false,
      fixed: false,
      items: [{
        icon: 'all_inbox',
        title: 'Home',
        route: { name: 'mailboxes' }
      }, {
        icon: 'mail',
        title: 'Compose message',
        route: { name: 'mailedit' }
      }, {
        icon: 'input',
        title: 'Log out',
        action: () => {
          this.logout()
        }
      }
      ],
      miniVariant: false,
      account: null
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">

.content{
  height: 100%;

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

</style>
