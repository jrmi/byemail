/* eslint-disable no-console */

import { register } from "register-service-worker";

function urlBase64ToUint8Array(base64String) {
  console.log(base64String);
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

if (process.env.NODE_ENV === "production") {
  register(`${process.env.BASE_URL}service-worker.js`, {
    ready(registration) {
      console.log(
        "App is being served from cache by a service worker.\n" +
          "For more details, visit https://goo.gl/AFskqB"
      );
      console.log(registration);
      registration.pushManager
        .getSubscription()
        .then(async function(subscription) {
          if (subscription) {
            console.log("Push already registered");
            return subscription;
          } else {
            console.log("New push registration");

            // Get public key from server
            const response = await fetch("./subscription/");
            const vapidPublicKey = await response.text();
            const convertedVapidKey = urlBase64ToUint8Array(vapidPublicKey);

            return registration.pushManager.subscribe({
              userVisibleOnly: true,
              applicationServerKey: convertedVapidKey
            });
          }
        })
        .then(
          function(subscription) {
            console.log("Send/update push subscription to server");
            fetch("/subscription/", {
              method: "post",
              headers: {
                "Content-type": "application/json"
              },
              body: JSON.stringify({
                subscription: subscription
              })
            });
          },
          function(failed) {
            console.log("Fail to push subscription to server: ", failed);
          }
        );
    },
    registered() {
      console.log("Service worker has been registered.");
    },
    cached() {
      console.log("Content has been cached for offline use.");
    },
    updatefound() {
      console.log("New content is downloading.");
    },
    updated() {
      console.log("New content is available; please refresh.");
    },
    offline() {
      console.log(
        "No internet connection found. App is running in offline mode."
      );
    },
    error(error) {
      console.error("Error during service worker registration:", error);
    }
  });
}
