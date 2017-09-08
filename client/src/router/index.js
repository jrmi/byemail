import Vue from 'vue'
import Router from 'vue-router'
import Hello from '@/components/Hello'
import Mailboxes from '@/components/Mailboxes'
import VueResource from 'vue-resource'
import VueMaterial from 'vue-material'
import 'vue-material/dist/vue-material.css'

Vue.use(Router)
Vue.use(VueResource)
Vue.use(VueMaterial)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Hello',
      component: Hello
    },
    {
      path: '/mailboxes/',
      name: 'Mailboxes',
      component: Mailboxes
    },
    {
      path: '/mailbox/:name',
      name: 'Mailbox',
      component: Mailboxes
    }
  ]
})
