<template>
  <LoadingOverlay v-if="store.getters.isLoading" />
  <router-view />
</template>

<script>
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import axios from 'axios';
import LoadingOverlay from './components/LoadingOverlay.vue';

// Set the root URL for axios globally
// axios.defaults.baseURL = 'https://fitpackvnapi.fitpack.io.vn/api/v1';
axios.defaults.baseURL = 'https://fitpackhnapi.fitpack.io.vn/api/v1';
// axios.defaults.baseURL = 'http://localhost:8000/api/v1';

export default {
  name: 'App',
  components: {
    LoadingOverlay,
  },
  setup() {
    const store = useStore();
    const router = useRouter();

    const checkTokenValidity = async () => {
      try {
        const response = await axios.get('/who_i_am/');
        // console.log('Token is valid:', response.data);

        const userGroups_ = response.data.usergroups || [];
        const isAdmin = userGroups_.includes('admin');
        store.dispatch('setUserAdmin', isAdmin);
        const isSuperadmin = userGroups_.includes('super_user');
        // console.log('userGroups_:', userGroups_);
        store.dispatch('setUserSuperadmin', isSuperadmin);
        // console.log('setUserAdmin:', isAdmin);
        // console.log('setUserSuperadmin:', isSuperadmin);
        // console.log('User groups:');
        store.dispatch('setUserName', response.data.username || '');
        // console.log('setUserName:', response.data.username || '');

      } catch (error) {
        console.error('Invalid token:', error);
        store.dispatch('removeToken'); // Clear token if invalid
        router.push('/signin'); // Redirect to SignIn page
      }
    };

    store.dispatch('checkAuthentication').then(() => {
      if (store.getters.isAuthenticated) {
        const token = store.getters.getToken;
        // console.log('Existing token found:', token);
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`; // Set default token header
        checkTokenValidity(); // Check token validity
        store.commit('setLoading', false); 
      } else {
        router.push('/signin'); // Redirect to SignIn page if not authenticated
        store.commit('setLoading', false);
      }
    });

    return {
      store,
    };
  },
};
</script>

<style lang="scss">
@import '../node_modules/bulma/';

:root {
  --bulma-body-overflow-y: hidden !important;
}

$kv-primary: #0070F4;
$size-sm: 4vh;
$main-bg-color: azure;

#app {
  height: 100%;
  max-height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
  overflow: visible; /* Ensure no clipping */
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  background-color: $main-bg-color;
  box-sizing: border-box;
  // border: 3px solid purple; /* Debugging border */
}
</style>
