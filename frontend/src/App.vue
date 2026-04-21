<script>
import LoginPage from './components/LoginPage.vue'
import RegisterPage from './components/RegisterPage.vue'

export default {
  components: { LoginPage, RegisterPage },
  data() {
    return {
      page: 'login',      // 'login' | 'register' | 'dashboard'
      currentUser: null
    }
  },
  methods: {
    onLoginSuccess(user) {
      this.currentUser = user
      this.page = 'dashboard'
    },
    onRegisterSuccess(user) {
      this.currentUser = user
      this.page = 'dashboard'
    },
    logout() {
      this.currentUser = null
      this.page = 'login'
    }
  }
}
</script>

<template>
  <main class="page">
    <LoginPage
      v-if="page === 'login'"
      @login-success="onLoginSuccess"
      @go-register="page = 'register'"
    />

    <RegisterPage
      v-else-if="page === 'register'"
      @register-success="onRegisterSuccess"
      @go-login="page = 'login'"
    />

    <section v-else class="card dashboard">
      <p class="greeting">Welcome, <strong>{{ currentUser.username }}</strong></p>
      <p class="sub">You are signed in as {{ currentUser.email }}</p>
      <button class="logout-btn" @click="logout">Sign Out</button>
    </section>
  </main>
</template>

<style scoped>
.page {
  min-height: 100svh;
  display: grid;
  place-items: center;
  padding: 20px;
  background: radial-gradient(circle at top left, #dbeafe 0%, #f0fdf4 55%, #fefce8 100%);
}

.card.dashboard {
  width: min(460px, 100%);
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  padding: 36px 32px;
  text-align: center;
  box-shadow: 0 16px 40px rgba(10, 30, 50, 0.1);
}

.greeting {
  margin: 0 0 6px;
  font-size: 22px;
  color: #0f172a;
}

.sub {
  margin: 0 0 24px;
  color: #64748b;
  font-size: 14px;
}

.logout-btn {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 10px 20px;
  background: #fff;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
}

.logout-btn:hover {
  background: #f9fafb;
}
</style>
