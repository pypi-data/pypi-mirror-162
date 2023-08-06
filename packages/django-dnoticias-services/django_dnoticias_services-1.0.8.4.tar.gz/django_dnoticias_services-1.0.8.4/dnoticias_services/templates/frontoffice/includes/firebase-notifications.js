const NOTIFICATION_COOKIE_NAME = "dn_fjs_notification";
const TOKEN_COOKIE_NAME = "dn_fjs_token"


function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
}


function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}


function sendTokenToServer(currentToken) {
    //if (!isTokenSentToServer()) {
        console.log('Sending token to server...');
        let tokenUrl = "https://dnoticias.loca.lt/api/token/create/"

        console.log("Current Token: ", currentToken);
        $.post({
            url: tokenUrl,
            data: {
            "token": currentToken,
            "fingerprint": fingerprint,
            "access_type": "web",
            },
            headers: {"X-FCM-APPLICATION-DOMAIN": "www.dnoticias.pt"},
        })
        .done(response => {
            console.log(response)
            setCookie(TOKEN_COOKIE_NAME, currentToken, 1)
            setupNotificationButton();
            //setTokenSentToServer(true);
        });
    // } else {
    //     console.log('Token already sent to server so won\'t send it again ' + 'unless it changes');
    // }
}


const subscribeDevice = (e) => {
    let apiUrl = "https://dnoticias.loca.lt/api/topic/subscribe/";
    let target = e.target || e.srcElement;
    let categorySlug = target.getAttribute("data-slug")
    $.post({
        url: apiUrl,
        data: {
            token: getCookie(TOKEN_COOKIE_NAME),
            topic_slug: categorySlug
        },
        headers: {"X-FCM-APPLICATION-DOMAIN": "www.dnoticias.pt"}
    })
    .done(response => {
        console.log(response)
        target.insertAdjacentHTML("afterend", getUnsubscribeHTML({slug: categorySlug}))
        target.remove();
        initializeEventListeners()
    })
    .catch(err => { console.error(err) })
}


const unsubscribeDevice = (e) => {
    let apiUrl = "https://dnoticias.loca.lt/api/topic/unsubscribe/";
    let target = e.target || e.srcElement;
    let categorySlug = target.getAttribute("data-slug")
    $.post({
        url: apiUrl,
        data: {
            token: getCookie(TOKEN_COOKIE_NAME),
            topic_slug: categorySlug
        },
        headers: {"X-FCM-APPLICATION-DOMAIN": "www.dnoticias.pt"}
    })
    .done(response => {
        console.log(response);
        target.insertAdjacentHTML("afterend", getSubscribeHTML({slug: categorySlug}))
        target.remove();
        initializeEventListeners()

    })
    .catch(err => { console.error(err) })
}


function getSubscribeHTML({slug}) {
    return `<span class="subscribeButton" data-slug="${slug}"> +</span>`
}


function getUnsubscribeHTML({slug}) {
    return `<span class="unsubscribeButton" data-slug="${slug}"> -</span>`
}


function initializeEventListeners() {
    let $unsubscribeButton = document.getElementsByClassName("unsubscribeButton")
    let $subscribeButton = document.getElementsByClassName("subscribeButton")

    for (var i = 0; i < $unsubscribeButton.length; i++) {
        $unsubscribeButton[i].addEventListener("click", unsubscribeDevice, false);
    }

    for (var i = 0; i < $subscribeButton.length; i++) {
        $subscribeButton[i].addEventListener("click", subscribeDevice, false);
    }
}


function loadSubscriptionButton({isSubscribed, $element, slug}) {
    if(isSubscribed) {
        $element.insertAdjacentHTML("afterend", getUnsubscribeHTML({slug}))
    } else {
        $element.insertAdjacentHTML("afterend", getSubscribeHTML({slug}))
    }

    initializeEventListeners();
}


function checkSubscribedDevice({categorySlug, $element}) {
    let apiUrl = "https://dnoticias.loca.lt/api/device/topic/";

    $.post({
        url: apiUrl,
        data: {
            token: getCookie(TOKEN_COOKIE_NAME),
            topic_slug: categorySlug
        },
        headers: {"X-FCM-APPLICATION-DOMAIN": "www.dnoticias.pt"}
    })
    .done((response) => {
        let isSubscribed = response.data.is_subscribed
        loadSubscriptionButton({isSubscribed, $element, slug: categorySlug})
    })
    .catch((err) => {
        console.error(err)
    })
}


function checkCategory($element) {
    let url = $element.getAttribute("href")

    if(url[url.length - 1] === '/'){
        url = url.slice(0, -1);
    }

    let categorySlug = url.split("/").pop();
    checkSubscribedDevice({categorySlug: categorySlug, $element: $element});
}


function setupNotificationButton() {
    let $categoriesWrapper = document.getElementsByClassName("article--aside_categories")[0];
    let $categories = $categoriesWrapper.getElementsByTagName("a")

    for($element of $categories) {
        checkCategory($element)
    }
}


const firebaseConfig = {
    apiKey: "AIzaSyAKW5I-bIiiMjSHzWZx-21OdM-5FITcU3g",
    authDomain: "dnoticias-d7.firebaseapp.com",
    projectId: "dnoticias-d7",
    storageBucket: "dnoticias-d7.appspot.com",
    messagingSenderId: "699426166670",
    appId: "1:699426166670:web:f2f5dd1ef2da55331636df",
    measurementId: "G-HXNR7YPPLJ"
};
// Initialize Firebase
firebase.initializeApp(firebaseConfig);
firebase.analytics();

// Retrieve Firebase Messaging object.
const messaging = firebase.messaging();

// Add the public key generated from the console here.
messaging.usePublicVapidKey("BLC1HglXCYQyj-RGsxaruOaT666pPaH5cXlCXv2S5-mba71c7jnR7aM6cTO5GqLklqqiD9Vs-Sw2fDPIg5hfpkg");

Notification.requestPermission().then((permission) => {
    if (permission === 'granted') {
        console.log('Notification permission granted.');
        // Get Instance ID token. Initially this makes a network call, once retrieved

        // subsequent calls to getToken will return from cache.
        messaging.getToken().then((currentToken) => {
            if (currentToken) {
                sendTokenToServer(currentToken);
            } else {
                // Show permission request.
                console.log('No Instance ID token available. Request permission to generate one.');
                //setTokenSentToServer(false);
            }
        }).catch((err) => {
            console.log('An error occurred while retrieving token. ', err);
            //setTokenSentToServer(false);
        });
    } else {
        var isFirefox = navigator.userAgent.toLowerCase().indexOf('firefox') > -1;
        if (isFirefox) {
            setupNotificationButton();
        } else {
            console.log('Unable to get permission to notify.');
        }
    }
});

// Callback fired if Instance ID token is updated.
messaging.onTokenRefresh(() => {
    messaging.getToken().then((refreshedToken) => {
        console.log('Token refreshed.');
        // Indicate that the new Instance ID token has not yet been sent to the
        // app server.
        // setTokenSentToServer(false);
        // Send Instance ID token to app server.
        sendTokenToServer(refreshedToken);
    }).catch((err) => {
        console.log('Unable to retrieve refreshed token ', err);
    });
});

messaging.onMessage(function(payload) {

    var url = payload.data.link;
    var parsedUrl = new URL(url);
    console.log("self.location.hostname: ", self.location.hostname);
    console.log("parsedUrl.hostname: ", parsedUrl.hostname);

    if (self.location.hostname != parsedUrl.hostname) return;

    navigator.serviceWorker.getRegistration('/firebase-cloud-messaging-push-scope').then(registration => {
        console.log("link:", payload.data.link);
        var options = {
            "data" : payload.data,
            "body" : payload.data.body,
            "icon" : payload.data.icon,
            "image" : payload.data.image,
            "click_action" : payload.data.link,
            "tag" : payload.data.link
        };
        registration.showNotification(
            payload.data.title,
            options,
        )
    });

});