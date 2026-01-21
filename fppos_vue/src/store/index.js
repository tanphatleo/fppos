import { createStore } from 'vuex';

export default createStore({
  state: {
    isAuthenticated: false,
    token: null,
    isLoading: false, // Add isLoading state
    user_admin: false, // Add user_admin state
    user_name : '', // Add user_name state
    user_superadmin: false, // Add user_superadmin state
  },
  getters: {
    isAuthenticated: (state) => state.isAuthenticated,
    getToken: (state) => state.token,
    isLoading: (state) => state.isLoading, // Getter for isLoading
    userAdmin: (state) => state.user_admin, // Getter for user_admin
    userName: (state) => state.user_name, // Getter for user_name
    userSuperadmin: (state) => state.user_superadmin, // Getter for user_superadmin
  },
  mutations: {
    setAuthentication(state, status) {
      state.isAuthenticated = status;
    },
    setToken(state, token) {
      state.token = token;
    },
    clearToken(state) {
      state.token = null;
    },
    setLoading(state, status) {
      state.isLoading = status; // Mutation to set isLoading
    },
    setUserAdmin(state, status) {
      state.user_admin = !!status;
    },
    setUserName(state, name) {
      state.user_name = name;
    },
    setUserSuperadmin(state, status) {
      state.user_superadmin = !!status;
    },
  },
  actions: {
    checkAuthentication({ commit }) {
      commit('setLoading', true); // Set loading to true
      const token = localStorage.getItem('token');
      if (token) {
        commit('setToken', token);
        commit('setAuthentication', true);
      } else {
        commit('clearToken');
        commit('setAuthentication', false);
      }
      commit('setLoading', false); // Set loading to false
    },

    setUserAdmin({ commit }, status) {
      commit('setUserAdmin', status);
    },
    
    setUserName({ commit }, name) {
      commit('setUserName', name);
    },

    setUserSuperadmin({ commit }, status) {
      commit('setUserSuperadmin', status);
    },

    setToken({ commit }, token) {
      commit('setLoading', true);
      localStorage.setItem('token', token);
      commit('setToken', token);
      commit('setAuthentication', true);
      commit('setLoading', false);

    },

    removeToken({ commit }) {
      commit('setLoading', true);
      localStorage.removeItem('token');
      commit('clearToken');
      commit('setAuthentication', false);
      commit('setLoading', false);
      commit('setUserAdmin', false);
      commit('setUserName', '');
      commit('setUserSuperadmin', false);
    },
  },
  modules: {},
});
