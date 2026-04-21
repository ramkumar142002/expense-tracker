<script>
export default {
  data() {
    return {
      backendStatus: 'Checking backend...',
      isSubmitting: false,
      form: {
        username: '',
        email: '',
        password: ''
      },
      users: [],
      errors: {
        username: '',
        email: '',
        password: '',
        api: ''
      },
      successMessage: ''
    }
  },
  async mounted() {
    try {
      const res = await fetch('http://127.0.0.1:8000/')
      const data = await res.json()
      this.backendStatus = data.message
      await this.fetchUsers()
    } catch (err) {
      this.backendStatus = 'Error connecting to backend'
      console.error(err)
    }
  },
  methods: {
    clearErrors() {
      this.errors = {
        username: '',
        email: '',
        password: '',
        api: ''
      }
    },
    validateForm() {
      this.clearErrors()
      let ok = true

      if (!this.form.username.trim()) {
        this.errors.username = 'Username is required.'
        ok = false
      }

      if (!this.form.email.trim()) {
        this.errors.email = 'Email is required.'
        ok = false
      } else if (!/^\S+@\S+\.\S+$/.test(this.form.email)) {
        this.errors.email = 'Enter a valid email.'
        ok = false
      }

      if (!this.form.password) {
        this.errors.password = 'Password is required.'
        ok = false
      } else if (this.form.password.length < 6) {
        this.errors.password = 'Password must be at least 6 characters.'
        ok = false
      }

      return ok
    },
    async fetchUsers() {
      const res = await fetch('http://127.0.0.1:8000/users')
      if (!res.ok) {
        throw new Error('Failed to fetch users')
      }
      this.users = await res.json()
    },
    async createUser() {
      this.successMessage = ''
      if (!this.validateForm()) {
        return
      }

      this.isSubmitting = true
      try {
        const res = await fetch('http://127.0.0.1:8000/users', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: this.form.username,
            email: this.form.email,
            password: this.form.password
          })
        })

        const data = await res.json()
        if (!res.ok) {
          this.errors.api = data.detail || 'Could not create user.'
          return
        }

        this.successMessage = `User ${data.username} created successfully.`
        this.form = {
          username: '',
          email: '',
          password: ''
        }
        await this.fetchUsers()
      } catch (err) {
        this.errors.api = 'Backend request failed.'
        console.error(err)
      } finally {
        this.isSubmitting = false
      }
    }
  }
}
</script>

<template>
  <main class="page">
    <section class="card">
      <p class="status">{{ backendStatus }}</p>
      <h1>Create User</h1>

      <form class="form" @submit.prevent="createUser">
        <label>
          Username
          <input v-model="form.username" type="text" placeholder="jane" />
          <small v-if="errors.username" class="error">{{ errors.username }}</small>
        </label>

        <label>
          Email
          <input v-model="form.email" type="email" placeholder="jane@email.com" />
          <small v-if="errors.email" class="error">{{ errors.email }}</small>
        </label>

        <label>
          Password
          <input v-model="form.password" type="password" placeholder="At least 6 chars" />
          <small v-if="errors.password" class="error">{{ errors.password }}</small>
        </label>

        <small v-if="errors.api" class="error">{{ errors.api }}</small>
        <button type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Creating...' : 'Create User' }}
        </button>
      </form>

      <p v-if="successMessage" class="success">{{ successMessage }}</p>

      <section class="users">
        <h2>Users</h2>
        <p v-if="users.length === 0">No users yet.</p>
        <ul v-else>
          <li v-for="user in users" :key="user.id">
            <strong>{{ user.username }}</strong>
            <span>{{ user.email }}</span>
          </li>
        </ul>
      </section>
    </section>
  </main>
</template>

<style scoped>
.page {
  min-height: 100svh;
  display: grid;
  place-items: center;
  padding: 20px;
  background: radial-gradient(circle at top left, #d6f0ff 0%, #fff7df 55%, #f6f9ff 100%);
}

.card {
  width: min(600px, 100%);
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 12px 30px rgba(10, 30, 50, 0.1);
}

.status {
  margin: 0;
  color: #475569;
  font-size: 14px;
}

h1 {
  margin: 8px 0 16px;
  font-size: 30px;
}

.form {
  display: grid;
  gap: 12px;
}

label {
  display: grid;
  gap: 6px;
  text-align: left;
  font-weight: 600;
}

input {
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  padding: 10px;
  font-size: 15px;
}

button {
  border: 0;
  border-radius: 10px;
  padding: 11px 14px;
  color: #fff;
  font-weight: 700;
  background: linear-gradient(95deg, #0369a1 0%, #0f766e 100%);
}

button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.error {
  color: #b91c1c;
}

.success {
  margin-top: 14px;
  color: #0f766e;
}

.users {
  margin-top: 22px;
  text-align: left;
}

h2 {
  margin: 0 0 10px;
}

ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
}

li {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 10px;
  flex-wrap: wrap;
}

li span {
  color: #475569;
}
</style>