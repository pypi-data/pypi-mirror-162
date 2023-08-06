<template>
  <form method="post" ref="form" :action="action" id="language-form">
    <v-text-field
      v-show="false"
      name="csrfmiddlewaretoken"
      :value="csrf_value"
      type="hidden"
    ></v-text-field>
    <v-text-field
      v-show="false"
      name="next"
      :value="next_url"
      type="hidden"
    ></v-text-field>
    <input
      name="language"
      :value="current_language"
      type="hidden"
    >
    <v-menu offset-y>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          depressed
          v-bind="attrs"
          v-on="on"
          color="primary"
        >
          <v-icon icon color="white">mdi-translate</v-icon>
          {{ current_language }}
        </v-btn>
      </template>
      <v-list id="language-dropdown" class="dropdown-content">
        <v-list-item-group
          v-model="current_language"
          color="primary"
        >
          <v-list-item v-for="language in items" :key="language[0]" :value="language[0]" @click="submit(language[0])">
            <v-list-item-title>{{ language[1] }}</v-list-item-title>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </v-menu>
  </form>
</template>

<script>
  export default {
    data: () => ({
        items: JSON.parse(document.getElementById("language-info-list").textContent),
        current_language: JSON.parse(document.getElementById("current-language").textContent),
    }),
    methods: {
        submit: function (language) {
            this.current_language = language;
            // this.$refs.form.submit()
        },
    },
    props: ["action", "csrf_value", "next_url"],
    name: "language-form",
  }
</script>
