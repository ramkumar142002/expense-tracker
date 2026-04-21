<script>
import LoginPage from './components/LoginPage.vue'
import RegisterPage from './components/RegisterPage.vue'
import DashboardPage from './components/DashboardPage.vue'

export default {
  components: { LoginPage, RegisterPage, DashboardPage },
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

    <DashboardPage
      v-else
      :current-user="currentUser"
      @logout="logout"
    />
  </main>
</template>

<style scoped>
.page {
  min-height: 100svh;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 20px;
  background: radial-gradient(circle at top left, #dbeafe 0%, #f0fdf4 55%, #fefce8 100%);
}
</style>
