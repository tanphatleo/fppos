<template>
  <div class="sign-in">
    <form @submit.prevent="handleSignIn">
      <h1>Sign In</h1>
      <div v-if="errors.length" class="error-messages">
        <ul>
          <li v-for="(error, index) in errors" :key="index" class="error">{{ error }}</li>
        </ul>
      </div>
      <div class="form-group">
        <label for="user">User</label>
        <input
          id="user"
          v-model="user"
          placeholder="Enter your user"
          required
        />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input
          type="password"
          id="password"
          v-model="password"
          placeholder="Enter your password"
          required
        />
      </div>
      <button type="submit" class="btn">Sign In</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: "SignIn",
  data() {
    return {
      user: "",
      password: "",
      errors: [],
    };
  },
  methods: {
    async handleSignIn() {
      this.errors = []; // Clear previous errors
      const formData = {
        username: this.user,
        password: this.password,
      };

      // remove old token
      this.$store.dispatch('setToken', null);
      axios.defaults.headers.common['Authorization'] = '';

      // await axios.post('/token/login', formData)
      await axios.post('/jwt/create/', formData)
        .then(response => {
          const token = response.data.access;
          this.$store.dispatch('setToken', token);
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;


          axios.get('/who_i_am/')
            .then(res => {
              const userGroups_ = res.data.usergroups || [];
              const isAdmin = userGroups_.includes('admin');
              this.$store.dispatch('setUserAdmin', isAdmin);
              this.$store.dispatch('setUserName', res.data.username || '');
            })
            .catch(err => {
              console.error('Error fetching user info after sign-in:', err);
            });

          this.$router.push('/manage'); // Redirect to manage page after sign-in
        })
        .catch(error => {
          console.error("Sign-in failed:", error);
          if (error.response && error.response.data) {
            // Display server-provided error messages
            this.errors.push(...Object.values(error.response.data));
          } else {
            this.errors.push("Sign-in failed. Please check your credentials.");
          }
        });
    },
  },
  beforeMount() {
    // If already authenticated, redirect to manage page
    if (this.$store.getters.isAuthenticated) {
      this.$router.push('/manage');
    }
  }
};
</script>

<style scoped>


input {
  background-color: white;
  color: black;
}

.sign-in {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f5f5;
}

form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h1 {
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  text-align: center;
}

.error-messages {
  margin-bottom: 1rem;
  color: red;
}

.error {
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}

button {
  width: 100%;
  padding: 0.75rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}
</style>