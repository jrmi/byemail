<template>
  <v-content>
    <v-container fluid fill-height>
      <v-layout justify-center>
        <v-flex xs12 sm6 offset-xm3>
          <v-card>
            <v-toolbar color="teal" dark>
              <v-toolbar-side-icon :to="{name: 'mailboxes'}">
                <v-icon>arrow_back</v-icon>
              </v-toolbar-side-icon>

              <v-toolbar-title>Settings</v-toolbar-title>
            </v-toolbar>

            <v-list two-line subheader>
              <v-subheader>General</v-subheader>

              <v-list-tile avatar>
                <v-list-tile-content>
                  <v-list-tile-title>Account name</v-list-tile-title>
                  <v-list-tile-sub-title>{{account.name}}</v-list-tile-sub-title>
                </v-list-tile-content>
              </v-list-tile>
            </v-list>

            <v-divider></v-divider>

            <v-list subheader two-line>
              <v-subheader>Application</v-subheader>

              <notification-button/>

              <v-list-tile avatar @click="install()">
                <v-list-tile-content>
                  <v-list-tile-title>Install</v-list-tile-title>
                  <v-list-tile-sub-title>Install byemail application</v-list-tile-sub-title>
                </v-list-tile-content>
              </v-list-tile>
              <!--v-list-tile @click>
                <v-list-tile-action>
                  <v-checkbox v-model="invites"></v-checkbox>
                </v-list-tile-action>

                <v-list-tile-content @click="invites = !invites">
                  <v-list-tile-title>Invites</v-list-tile-title>
                  <v-list-tile-sub-title>Notify when receiving invites</v-list-tile-sub-title>
                </v-list-tile-content>
              </v-list-tile-->
            </v-list>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
  </v-content>
</template>

<script>
import { mapActions } from 'vuex'
import { deferredPrompt } from '../registerServiceWorker.js'
import NotificationButton from '@/components/NotificationButton'

export default {
  data() {
    return {
      account: { name: '' },
      installable: false
    }
  },
  components: {
    NotificationButton
  },
  created() {
    this.fetchData()
    this.installable = deferredPrompt !== null
  },
  methods: {
    install() {
      if (this.installable) {
        console.log('install')
        deferredPrompt.prompt()
        deferredPrompt.userChoice.then(choiceResult => {
          if (choiceResult.outcome === 'accepted') {
            console.log('User accepted to install application')
          } else {
            console.log('User dismissed installation')
          }
          deferredPrompt = null
        })
      } else {
        console.log('Cant be installed')
      }
    },

    fetchData() {
      this.setLoading(true)
      const userId = this.$route.params.userId
      this.$http.get(`/api/users/${userId}/account`).then(
        response => {
          this.account = response.body
          this.setLoading(false)
        },
        response => {
          this.$router.push({ name: 'login' })
          this.setLoading(false)
        }
      )
    },

    ...mapActions(['setLoading'])
  }
}
</script>

<style scoped lang="less">
.login {
  display: flex;
  flex-direction: column;
  align-items: center;
  .inside {
    display: block;
    flex: 1;
    width: 33%;
    min-width: 300px;
    padding: 10px;
    margin-top: 10px;
  }
}
</style>
