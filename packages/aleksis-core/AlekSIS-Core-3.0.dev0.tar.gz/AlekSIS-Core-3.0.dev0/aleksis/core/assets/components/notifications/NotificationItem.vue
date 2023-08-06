<template>
  <ApolloMutation
    :mutation="require('./markNotificationRead.graphql')"
    :variables="{ id: this.notification.id }"
  >
    <template v-slot="{ mutate, loading, error }">
      <v-list-item
        v-intersect="mutate"
      >
        <v-list-item-content>
          <v-list-item-title>{{ notification.title }}</v-list-item-title>

          <v-list-item-subtitle>
            <v-icon>mdi-clock-outline</v-icon>
            {{ notification.created }}
          </v-list-item-subtitle>

          <v-list-item-subtitle>
            {{ notification.description }}
          </v-list-item-subtitle>
        </v-list-item-content>

        <v-list-item-action v-if="notification.link">
          <v-btn text :href="notification.link">
            {{ this.$root.django.gettext('More information →') }}
          </v-btn>
        </v-list-item-action>

        <v-list-item-icon>
          <v-chip color="primary">{{ notification.sender }}</v-chip>
        </v-list-item-icon>
      </v-list-item>
    </template>
  </ApolloMutation>
</template>

<script>
  export default {
    props: {
      notification: Object,
    },
  }
</script>
