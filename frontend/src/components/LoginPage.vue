<script>
import { apiRequest } from '../api'

export default {
  emits: ['login-success', 'go-register'],
  data() {
    return {
      form: { username: '', password: '' },
      errors: { username: '', password: '', api: '' },
      isSubmitting: false
    }
  },
  methods: {
    validateForm() {
      this.errors = { username: '', password: '', api: '' }
      let ok = true
      if (!this.form.username.trim()) {
        this.errors.username = 'Username is required.'
        ok = false
      }
      if (!this.form.password) {
        this.errors.password = 'Password is required.'
        ok = false
      }
      return ok
    },
    async submit() {
      if (!this.validateForm()) return
      this.isSubmitting = true
      try {
        const data = await apiRequest('/login', {
          method: 'POST',
          body: JSON.stringify({
            username: this.form.username.trim(),
            password: this.form.password,
          }),
        })
        this.$emit('login-success', data)
      } catch (err) {
        this.errors.api = err?.message || 'Could not reach backend.'
      } finally {
        this.isSubmitting = false
      }
    }
  }
}
</script>

<template>
  <div class="card">
    <h1>Welcome back</h1>
    <p class="sub">Sign in to your account</p>

    <form class="form" @submit.prevent="submit">
      <label>
        Username
        <input v-model="form.username" type="text" placeholder="your username" autocomplete="username" />
        <small v-if="errors.username" class="error">{{ errors.username }}</small>
      </label>

      <label>
        Password
        <input v-model="form.password" type="password" placeholder="your password" autocomplete="current-password" />
        <small v-if="errors.password" class="error">{{ errors.password }}</small>
      </label>

      <small v-if="errors.api" class="error api-error">{{ errors.api }}</small>

      <button type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? 'Signing in...' : 'Sign In' }}
      </button>
    </form>

    <p class="switch">
      Don't have an account?
      <button class="link-btn" type="button" @click="$emit('go-register')">Create one</button>
    </p>
  </div>
</template>

<style scoped>
.card {
  width: min(460px, 100%);
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  padding: 36px 32px;
  box-shadow: 0 16px 40px rgba(10, 30, 50, 0.1);
}

h1 {
  margin: 0 0 4px;
  font-size: 28px;
  color: #0f172a;
}

.sub {
  margin: 0 0 24px;
  color: #64748b;
  font-size: 14px;
}

.form {
  display: grid;
  gap: 14px;
}

label {
  display: grid;
  gap: 6px;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

input {
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 15px;
  transition: border-color 0.2s;
}

input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

button[type='submit'] {
  margin-top: 4px;
  border: 0;
  border-radius: 10px;
  padding: 11px;
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(95deg, #4f46e5 0%, #0891b2 100%);
  cursor: pointer;
  transition: opacity 0.2s;
}

button[type='submit']:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: #dc2626;
  font-size: 12px;
  font-weight: 500;
}

.api-error {
  text-align: center;
}

.switch {
  margin: 20px 0 0;
  font-size: 14px;
  color: #64748b;
  text-align: center;
}

.link-btn {
  background: none;
  border: none;
  color: #4f46e5;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  font-size: inherit;
  text-decoration: underline;
}
</style>
