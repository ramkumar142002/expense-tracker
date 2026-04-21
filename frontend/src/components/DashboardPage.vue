<script>
import { apiRequest } from '../api'

export default {
  props: {
    currentUser: {
      type: Object,
      required: true,
    },
  },
  emits: ['logout'],
  data() {
    return {
      categories: [],
      expenses: [],
      newCategoryName: '',
      categoryError: '',
      expenseError: '',
      successMessage: '',
      isLoading: false,
      expenseForm: {
        category_id: '',
        description: '',
        amount: '',
        date: new Date().toISOString().slice(0, 10),
      },
    }
  },
  computed: {
    authHeaders() {
      return {
        'X-User-Id': String(this.currentUser.id),
      }
    },
  },
  methods: {
    async loadData() {
      this.isLoading = true
      this.categoryError = ''
      this.expenseError = ''
      try {
        const [categories, expenses] = await Promise.all([
          apiRequest('/categories', { headers: this.authHeaders }),
          apiRequest('/expenses', { headers: this.authHeaders }),
        ])
        this.categories = categories
        this.expenses = expenses
      } catch (err) {
        this.expenseError = err?.message || 'Failed to load dashboard data.'
      } finally {
        this.isLoading = false
      }
    },
    async addCategory() {
      this.categoryError = ''
      this.successMessage = ''
      const name = this.newCategoryName.trim()
      if (!name) {
        this.categoryError = 'Category name is required.'
        return
      }

      try {
        const newCategory = await apiRequest('/categories', {
          method: 'POST',
          headers: this.authHeaders,
          body: JSON.stringify({ name }),
        })
        this.categories = [...this.categories, newCategory].sort((a, b) => a.name.localeCompare(b.name))
        this.newCategoryName = ''
        this.successMessage = 'Category created.'
      } catch (err) {
        this.categoryError = err?.message || 'Could not create category.'
      }
    },
    async addExpense() {
      this.expenseError = ''
      this.successMessage = ''

      if (!this.expenseForm.category_id) {
        this.expenseError = 'Please select a category.'
        return
      }
      if (!this.expenseForm.amount || Number(this.expenseForm.amount) <= 0) {
        this.expenseError = 'Amount must be greater than 0.'
        return
      }
      if (!this.expenseForm.date) {
        this.expenseError = 'Date is required.'
        return
      }

      try {
        const expense = await apiRequest('/expenses', {
          method: 'POST',
          headers: this.authHeaders,
          body: JSON.stringify({
            category_id: Number(this.expenseForm.category_id),
            description: this.expenseForm.description.trim() || null,
            amount: Number(this.expenseForm.amount),
            date: this.expenseForm.date,
          }),
        })
        this.expenses = [expense, ...this.expenses]
        this.expenseForm.description = ''
        this.expenseForm.amount = ''
        this.successMessage = 'Expense added.'
      } catch (err) {
        this.expenseError = err?.message || 'Could not add expense.'
      }
    },
    formatAmount(value) {
      return Number(value).toFixed(2)
    },
  },
  mounted() {
    this.loadData()
  },
}
</script>

<template>
  <section class="dashboard-wrap">
    <header class="topbar">
      <div>
        <p class="greeting">Hi, <strong>{{ currentUser.username }}</strong></p>
        <p class="sub">{{ currentUser.email }} | {{ currentUser.is_superuser ? 'Super user' : 'User' }}</p>
      </div>
      <button class="logout-btn" @click="$emit('logout')">Sign Out</button>
    </header>

    <p v-if="successMessage" class="ok">{{ successMessage }}</p>

    <section v-if="currentUser.is_superuser" class="card block">
      <h2>Add Category</h2>
      <div class="form-row">
        <input v-model="newCategoryName" type="text" placeholder="Category name" />
        <button @click="addCategory">Add Category</button>
      </div>
      <p v-if="categoryError" class="error">{{ categoryError }}</p>
    </section>

    <section class="card block">
      <h2>Add Expense</h2>
      <div class="grid">
        <label>
          Category
          <select v-model="expenseForm.category_id">
            <option disabled value="">Select category</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
        </label>

        <label>
          Amount
          <input v-model="expenseForm.amount" type="number" min="0" step="0.01" placeholder="0.00" />
        </label>

        <label>
          Date
          <input v-model="expenseForm.date" type="date" />
        </label>

        <label class="desc">
          Description
          <textarea v-model="expenseForm.description" rows="2" placeholder="Optional note" />
        </label>
      </div>

      <button class="primary" @click="addExpense">Add Expense</button>
      <p v-if="expenseError" class="error">{{ expenseError }}</p>
      <p v-if="!currentUser.is_superuser && !categories.length" class="hint">
        No categories available. A super user needs to create categories first.
      </p>
    </section>

    <section class="card block">
      <h2>Your Expenses</h2>
      <p v-if="isLoading">Loading...</p>
      <ul v-else-if="expenses.length" class="expense-list">
        <li v-for="expense in expenses" :key="expense.id">
          <div>
            <p class="item-title">{{ expense.category_name || expense.name }}</p>
            <p class="item-sub">{{ expense.description || 'No description' }} | {{ expense.date }}</p>
          </div>
          <strong>${{ formatAmount(expense.amount) }}</strong>
        </li>
      </ul>
      <p v-else class="hint">No expenses added yet.</p>
    </section>
  </section>
</template>

<style scoped>
.dashboard-wrap {
  width: min(860px, 100%);
  display: grid;
  gap: 14px;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.greeting {
  margin: 0 0 2px;
  color: #0f172a;
  font-size: 20px;
}

.sub {
  margin: 0;
  color: #64748b;
  font-size: 13px;
}

.card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 16px;
}

.block h2 {
  margin: 0 0 10px;
  font-size: 18px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.desc {
  grid-column: 1 / -1;
}

label {
  display: grid;
  gap: 6px;
  font-size: 13px;
  color: #334155;
}

input,
select,
textarea {
  border: 1px solid #d1d5db;
  border-radius: 10px;
  padding: 9px 10px;
  font-size: 14px;
}

button {
  border: 0;
  border-radius: 10px;
  padding: 10px 14px;
  background: #1d4ed8;
  color: #fff;
  font-weight: 700;
  cursor: pointer;
}

.primary {
  margin-top: 10px;
}

.logout-btn {
  background: #0f172a;
}

.expense-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
}

.expense-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.item-title {
  margin: 0;
  font-weight: 700;
}

.item-sub {
  margin: 2px 0 0;
  font-size: 12px;
  color: #64748b;
}

.error {
  color: #dc2626;
  margin: 8px 0 0;
  font-size: 13px;
}

.ok {
  color: #166534;
  margin: 0;
  font-size: 13px;
}

.hint {
  margin: 8px 0 0;
  color: #64748b;
  font-size: 13px;
}

@media (max-width: 760px) {
  .grid {
    grid-template-columns: 1fr;
  }

  .topbar {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
