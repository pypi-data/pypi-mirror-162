<template>
  <ApolloQuery
    :query="require('./myNotifications.graphql')"
    :pollInterval="1000"
  >
    <template v-slot="{ result: { error, data }, isLoading }">
      <v-list two-line v-if="data && data.myNotifications.notifications">
        <NotificationItem
          v-for="notification in data.myNotifications.notifications"
          :key="notification.id"
          :notification="notification"
        />
      </v-list>
      <p v-else>{{ this.$root.django.gettext('No notifications available yet.') }}</p>
    </template>
  </ApolloQuery>
</template>

<script>
  import NotificationItem from "./NotificationItem.vue";

  export default {
    components: {
      NotificationItem,
    },
  }
</script>
