/* global describe it expect cy before after beforeEach afterEach */

const BASE_URL = 'http://192.168.0.20:8080/'

describe('Basic Tests', function() {
  it('See homepage', function() {
    cy.visit(BASE_URL)
    cy.contains('Login')
  })

  it('Login to mailbox', function() {
    cy.visit(BASE_URL)
    cy.contains('Login')

    // Login part
    cy.get('input[aria-label=Login]')
      .type('test')
      .should('have.value', 'test')
    cy.get('input[aria-label=Password]').type('test')
    cy.contains('Submit').click()

    cy.url().should('include', '/webmail/test/mailboxes')
  })
})

describe('Logged tests', function() {
  beforeEach(function() {
    cy.visit(BASE_URL)
    cy.contains('Login')

    // Login part
    cy.get('input[aria-label=Login]')
      .type('test')
      .should('have.value', 'test')
    cy.get('input[aria-label=Password]').type('test')
    cy.contains('Submit').click()
  })

  it('Can see mails', function() {
    cy.get('.mailboxlist')
      .contains('Suzie')
      .click()

    cy.contains('Mailbox: Suzie')

    cy.get('.maillist')
      .contains('First mail')
      .click()

    cy.contains('read me')

    cy.get('.maillist')
      .contains('Second mail')
      .click()

    cy.contains('Yes sure')

    cy.get('.mailboxlist')
      .contains('Sam')
      .click()

    cy.contains('Mailbox: Sam')
  })

  it('Can mark read mail', function() {
    cy.get('.mailboxlist')
      .contains('Sam')
      .click()

    cy.contains('Mailbox: Sam')

    cy.get('.maillist')
      .contains('My mail')
      .click()

    cy.get('.mail')
      .contains('visibility')
      .click()

    cy.get('.mail')
      .not()
      .contains('visibility')
  })
})

describe('Can write emails', function() {
  beforeEach(function() {
    cy.visit(BASE_URL)
    cy.contains('Login')

    // Login part
    cy.get('input[aria-label=Login]')
      .type('test')
      .should('have.value', 'test')
    cy.get('input[aria-label=Password]').type('test')
    cy.contains('Submit').click()
  })

  it('Can respond mail', function() {
    cy.get('.mailboxlist')
      .contains('Sam')
      .click()

    cy.contains('Mailbox: Sam')

    cy.get('.maillist .incoming')
      .contains('My mail')
      .click()

    cy.get('.mail')
      .contains('reply')
      .click()

    cy.get('.mail-compose textarea').type('Answer')

    cy.get('.mail-compose')
      .contains('send')
      .click()

    //cy.get('.maillist > div:first', { timeout: 10000 }).contains('Re: My mail')
    cy.get('.maillist', { timeout: 10000 })
      .contains('Re: My mail')
      .parent()
      .contains('a few seconds ago')
  })

  it('Can write new email', function() {
    cy.get('.mailboxlist')
      .contains('email')
      .click()

    cy.url().should('include', '/mailedit')

    // Add to
    cy.get('.recipients:first .layout > div:nth-child(2)')
      .find('input')
      .type('sam')
    cy.get('.v-autocomplete__content')
      .contains('sam@example.com')
      .click()

    // Add cc
    cy.contains('Add recipient').click()
    cy.get('.recipients:nth-child(2) .layout > div:first')
      .contains('arrow_drop_down')
      .click()

    cy.get('.v-menu__content')
      .contains('Cc')
      .click()

    cy.get('.recipients:nth-child(2) .layout > div:nth-child(2)')
      .find('input')
      .type('suz')

    cy.get('.v-autocomplete__content')
      .contains('suzie@example.com')
      .click()

    // Write subject and content
    cy.contains('Subject')
      .parent()
      .find('input')
      .type('My subject')
    cy.contains('Content')
      .parent()
      .find('textarea')
      .type('My content')

    // Send
    cy.contains('Send').click()

    cy.url().should('include', '/mailboxes')

    cy.get('.mailboxlist')
      .contains('Suzie')
      .click()

    cy.get('.maillist > div:first').contains('My subject')

    cy.get('.mailboxlist')
      .contains('Sam')
      .click()

    cy.get('.maillist > div:first').contains('My subject')
  })
})
