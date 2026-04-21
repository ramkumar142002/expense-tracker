<script>
import { apiRequest } from '../api'

export default {
  emits: ['register-success', 'go-login'],
  data() {
    return {
      form: { username: '', email: '', password: '', is_superuser: false },
      errors: { username: '', email: '', password: '', api: '' },
      isSubmitting: false
    }
  },
  methods: {
    validateForm() {
      this.errors = { username: '', email: '', password: '', api: '' }
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
    async submit() {
      if (!this.validateForm()) return
      this.isSubmitting = true
      try {
        const data = await apiRequest('/users', {
          method: 'POST',
          body: JSON.stringify({
            username: this.form.username.trim(),
            email: this.form.email.trim().toLowerCase(),
            password: this.form.password,
            is_superuser: this.form.is_superuser,
          }),
        })
        this.$emit('register-success', data)
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
    <h1>Create account</h1>
    <p class="sub">Fill in your details to get started</p>

    <form class="form" @submit.prevent="submit">
      <label>
        Username
        <input v-model="form.username" type="text" placeholder="jane_doe" autocomplete="username" />
        <small v-if="errors.username" class="error">{{ errors.username }}</small>
      </label>

      <label>
        Email
        <input v-model="form.email" type="email" placeholder="jane@email.com" autocomplete="email" />
        <small v-if="errors.email" class="error">{{ errors.email }}</small>
      </label>

      <label>
        Password
        <input v-model="form.password" type="password" placeholder="At least 6 characters" autocomplete="new-password" />
        <small v-if="errors.password" class="error">{{ errors.password }}</small>
      </label>

      <label class="checkbox-row">
        <input v-model="form.is_superuser" type="checkbox" />
        Create as super user
      </label>

      <small v-if="errors.api" class="error api-error">{{ errors.api }}</small>

      <button type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? 'Creating...' : 'Create Account' }}
      </button>
    </form>

    <p class="switch">
      Already have an account?
      <button class="link-btn" type="button" @click="$emit('go-login')">Sign in</button>
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

.checkbox-row {
  grid-template-columns: 16px 1fr;
  align-items: center;
  gap: 10px;
  font-weight: 500;
}

.checkbox-row input[type='checkbox'] {
  width: 16px;
  height: 16px;
  margin: 0;
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
  background: linear-gradient(95deg, #0f766e 0%, #0369a1 100%);
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
  color: #0f766e;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  font-size: inherit;
  text-decoration: underline;
}
</style>
