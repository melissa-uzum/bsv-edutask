describe('Managing todo items for a task (R8)', () => {
  let uid // user id
  let email // email of the user
  let name // name of the user

  before(function () {
    // create a fabricated user from a fixture
    cy.fixture('user.json')
      .then((user) => {
        cy.request({
          method: 'POST',
          url: 'http://localhost:5000/users/create',
          form: true,
          body: user
        }).then((response) => {
          uid = response.body._id.$oid
          email = user.email
          name = user.firstName + ' ' + user.lastName

          // create a task with one default todo item for this user
          cy.request({
            method: 'POST',
            url: 'http://localhost:5000/tasks/create',
            form: true,
            body: {
              title: 'Test Task',
              description: 'A task for testing todo operations',
              userid: uid,
              url: 'dQw4w9WgXcQ',
              todos: JSON.stringify(['Watch video'])
            }
          })
        })
      })
  })

  beforeEach(function () {
    // visit the app and log in
    cy.visit('http://localhost:3000')
    cy.contains('div', 'Email Address')
      .find('input[type=text]')
      .type(email)
    cy.get('form').submit()

    // wait for the task view to load
    cy.get('h1').should('contain.text', name)

    // open the task in detail view by clicking on it
    cy.contains('.title-overlay', 'Test Task').click()

    // wait for the popup to be visible
    cy.get('.popup').should('be.visible')
  })

  // =============================================
  // R8UC1: Create a new todo item
  // =============================================
  describe('R8UC1: Create a new todo item', () => {
    it('should add a new active todo item with the given description', () => {
      // get the initial number of todo items
      cy.get('.todo-item').its('length').then((initialCount) => {
        // enter a description in the input field
        cy.get('.inline-form input[type="text"]')
          .type('New test todo')

        // click the Add button
        cy.get('.inline-form input[type="submit"]')
          .click()

        // verify that one more todo item appeared
        cy.get('.todo-item')
          .should('have.length', initialCount + 1)

        // verify the new todo is at the bottom with the correct text
        cy.get('.todo-item').last()
          .should('contain.text', 'New test todo')

        // verify the new todo item is active (unchecked)
        cy.get('.todo-item').last()
          .find('.checker')
          .should('have.class', 'unchecked')
      })
    })

    it('should have the Add button disabled when description is empty', () => {
      // verify the input field is empty
      cy.get('.inline-form input[type="text"]')
        .should('have.value', '')

      // per R8UC1 2.b, the Add button should remain disabled when description is empty
      cy.get('.inline-form input[type="submit"]')
        .should('be.disabled')
    })
  })

  // =============================================
  // R8UC2: Toggle a todo item
  // =============================================
  describe('R8UC2: Toggle a todo item', () => {
    it('should set an active todo item to done (struck through)', () => {
      // click the checker icon of the first unchecked todo item
      cy.get('.todo-item .checker.unchecked').first()
        .click()

      // verify the checker is now in the checked state
      cy.get('.todo-item').first()
        .find('.checker')
        .should('have.class', 'checked')

      // verify the todo text is struck through
      cy.get('.todo-item').first()
        .find('.editable')
        .should('have.css', 'text-decoration')
        .and('include', 'line-through')
    })

    it('should set a done todo item back to active (not struck through)', () => {
      // click the checker icon of the first checked todo item
      cy.get('.todo-item .checker.checked').first()
        .click()

      // verify the checker is now in the unchecked state
      cy.get('.todo-item').first()
        .find('.checker')
        .should('have.class', 'unchecked')

      // verify the todo text is no longer struck through
      cy.get('.todo-item').first()
        .find('.editable')
        .should('have.css', 'text-decoration')
        .and('not.include', 'line-through')
    })
  })

  // =============================================
  // R8UC3: Delete a todo item
  // =============================================
  describe('R8UC3: Delete a todo item', () => {
    it('should remove a todo item when clicking the delete button', () => {
      // get the initial number of todo items
      cy.get('.todo-item').its('length').then((initialCount) => {
        // click the delete button (✖) of the first todo item
        cy.get('.todo-item .remover').first()
          .click()

        // verify that one less todo item is in the list
        cy.get('.todo-item')
          .should('have.length', initialCount - 1)
      })
    })
  })

  after(function () {
    // clean up by deleting the user from the database
    cy.request({
      method: 'DELETE',
      url: `http://localhost:5000/users/${uid}`
    }).then((response) => {
      cy.log(response.body)
    })
  })
})
