if (workbox) {
  console.log(`Yay! Workbox is loaded 🎉`)
} else {
  console.log(`Boo! Workbox didn't load 😬`)
}

// Register event listener for the 'push' event.
self.addEventListener('push', function (event) {
  console.log('Get a push')
  // Retrieve the textual payload from event.data (a PushMessageData object).
  // Other formats are supported (ArrayBuffer, Blob, JSON), check out the documentation
  // on https://developer.mozilla.org/en-US/docs/Web/API/PushMessageData.
  const payload = event.data ? event.data.text() : 'You have a new message'

  event.waitUntil(
    // Retrieve a list of the clients of this service worker.
    self.clients.matchAll().then(function (clientList) {
      // Check if there's at least one focused client.
      var focused = clientList.some(function (client) {
        return client.focused
      })

      if (focused) {
        // Focused
      } else if (clientList.length > 0) {
        // Click to focus
      } else {
        // Reopen
      }

      return self.registration.showNotification('Byemail', {
        body: payload,
        tag: 'newmail'
      })
    })
  )
})

// Register event listener for the 'notificationclick' event.
self.addEventListener('notificationclick', function (event) {
  console.log('notif click')
  event.waitUntil(
    // Retrieve a list of the clients of this service worker.
    self.clients.matchAll().then(function (clientList) {
      console.log('clients', clientList)
      // If there is at least one client, focus it.
      if (clientList.length > 0) {
        return clientList[0].focus()
      }

      // Otherwise, open a new page.
      return self.clients.openWindow('/index.html')
    })
  )
})
