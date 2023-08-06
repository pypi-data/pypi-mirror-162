import Vue from "vue"
import VueRouter from "vue-router"
import Vuetify from "vuetify"
import "vuetify/dist/vuetify.min.css"

import ApolloClient from 'apollo-boost'
import VueApollo from 'vue-apollo'

Vue.use(Vuetify)
Vue.use(VueRouter)

const vuetify = new Vuetify({
    // TODO: load theme data dynamically
    //  - find a way to load template context data
    //  - include all site preferences
    //  - load menu stuff to render the sidenav
    icons: {
        iconfont: 'mdi', // default - only for display purposes
        values: {
          cancel: 'mdi-close-circle-outline',
          delete: 'mdi-close-circle-outline',
          success: 'mdi-check-circle-outline',
          info: 'mdi-information-outline',
          warning: 'mdi-alert-outline',
          error: 'mdi-alert-octagon-outline',
          prev: 'mdi-chevron-left',
          next: 'mdi-chevron-right',
          checkboxOn: 'mdi-checkbox-marked-outline',
          checkboxIndeterminate: 'mdi-minus-box-outline',
          edit: 'mdi-pencil-outline',
        },
    },
    theme: {
        dark: JSON.parse(document.getElementById("design-mode").textContent) === "dark",
        themes: {
            light: {
                primary: JSON.parse(document.getElementById("primary-color").textContent),
                secondary: JSON.parse(document.getElementById("secondary-color").textContent),
            },
            dark: {
                primary: JSON.parse(document.getElementById("primary-color").textContent),
                secondary: JSON.parse(document.getElementById("secondary-color").textContent),
            },
        },
    },
    lang: {
        locales: JSON.parse(document.getElementById("language-info-list").textContent),
        current: JSON.parse(document.getElementById("current-language").textContent),
    }
})

const apolloClient = new ApolloClient({
  uri: JSON.parse(document.getElementById("graphql-url").textContent)
})

import CacheNotification from "./components/CacheNotification.vue";
import LanguageForm from "./components/LanguageForm.vue";
import MessageBox from "./components/MessageBox.vue";
import NotificationList from "./components/notifications/NotificationList.vue";
import SidenavSearch from "./components/SidenavSearch.vue";

Vue.component(MessageBox.name, MessageBox); // Load MessageBox globally as other components depend on it

Vue.use(VueApollo)

const apolloProvider = new VueApollo({
  defaultClient: apolloClient,
})

const router = new VueRouter({
  mode: "history",
//  routes: [
//    { path: "/", component: "TheApp" },
//  }
});

const app = new Vue({
    el: '#app',
    apolloProvider,
    vuetify: vuetify,
    // delimiters: ["<%","%>"] // FIXME: discuss new delimiters, [[ <% [{ {[ <[ (( …
    data: () => ({
        drawer: vuetify.framework.breakpoint.lgAndUp,
        group: null, // what does this mean?
        urls: window.Urls,
        django: window.django,
        // FIXME: maybe just use window.django in every component or find a suitable way to access this property everywhere
        showCacheAlert: false,
        languageCode: JSON.parse(document.getElementById("current-language").textContent),
    }),
    components: {
        "cache-notification": CacheNotification,
        "language-form": LanguageForm,
        "notification-list": NotificationList,
        "sidenav-search": SidenavSearch,
    },
    router
})

window.app = app;
window.router = router;
