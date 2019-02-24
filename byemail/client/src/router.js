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
      redirect: { name: 'mailboxes' }
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/webmail/:userId',
      name: 'webmail',
      component: Webmail,
      children: [
        {
          path: 'mailboxes/',
          name: 'mailboxes',
          components: {
            default: Mailboxes
          },
          children: [
            {
              path: 'mailbox/:mailboxId',
              name: 'mailbox',
              components: {
                default: Mailbox
              }
            },
            {
              path: 'mailbox/:mailboxId/mail/:mailId',
              name: 'mail',
              components: {
                default: Mailbox,
                mail: Mail
              }
            }
          ]
        },
        {
          path: 'mailedit',
          name: 'mailedit',
          component: MailEdit
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
