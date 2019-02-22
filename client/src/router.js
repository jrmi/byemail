import Vue from 'vue'
import Router from 'vue-router'
import Login from '@/views/Login'
import Webmail from '@/views/Webmail'
import Mailboxes from '@/views/Mailboxes'
import Mailbox from '@/views/Mailbox'
import Mail from '@/views/Mail'
import MailEdit from '@/views/MailEdit'
import Settings from '@/views/Settings'

Vue.use(Router)

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
      path: '/webmail',
      name: 'webmail',
      component: Webmail,
      children: [
        {
          path: '/mailboxes/',
          name: 'mailboxes',
          components: {
            default: Mailboxes
          },
          children: [
            {
              path: 'mailbox/:id',
              name: 'mailbox',
              components: {
                default: Mailbox
              }
            },
            {
              path: 'mailbox/:id/mail/:mail_id',
              name: 'mail',
              components: {
                default: Mailbox,
                mail: Mail
              }
            }
          ]
        },
        {
          path: '/mailedit',
          name: 'mailedit',
          component: MailEdit
        },
        {
          path: '/config',
          name: 'config',
          component: null
        }
      ]
    },
    {
      path: '/settings',
      name: 'settings',
      component: Settings
    }
  ]
})
