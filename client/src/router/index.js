import Vue from 'vue'
import Router from 'vue-router'
import Login from '@/components/Login'
import Mailboxes from '@/components/Mailboxes'
import Mailbox from '@/components/Mailbox'
import Mail from '@/components/Mail'
import VueResource from 'vue-resource'
import VueMaterial from 'vue-material'
import 'vue-material/dist/vue-material.css'
import 'material-icons/css/material-icons.css'

Vue.use(Router)
Vue.use(VueResource)
Vue.use(VueMaterial)

export default new Router({
  routes: [
    {
      path: '/',
      redirect: { name: 'login' }
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/mailboxes/',
      name: 'mailboxes',
      component: Mailboxes,
      children: [
        {
          path: 'show_mailbox/:id',
          name: 'mailbox',
          component: Mailbox,
          children: [
            {
              path: 'show_mail/:mail_id',
              name: 'mail',
              component: Mail
            }
          ]
        }
      ]
    }
  ]
})
