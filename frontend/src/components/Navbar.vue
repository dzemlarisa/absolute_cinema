<template>
    <header class="navbar">
        <div class="container">
            <div class="logo">
                <router-link to="/">Absolute Cinema</router-link>
            </div>
            <nav class="nav-links">
                <router-link to="/" class="nav-link">Главная</router-link>
                <router-link to="/movies" class="nav-link">Фильмы</router-link>
                <router-link to="/cinemas" class="nav-link">Кинотеатры</router-link>
                <router-link to="/sessions" class="nav-link">Сеансы</router-link>
                <router-link to="/ticket" class="nav-link">Купить билет</router-link>
            </nav>
            <div class="auth-buttons">
                <button v-if="!isAuthenticated" class="btn-auth" @click="showLoginModal = true">
                    <i class="fas fa-user-circle"></i> Вход
                </button>
                <div v-else class="user-menu">
                    <span v-if="isAdmin" class="admin-badge">Администратор</span>
                    <span class="user-name">{{ userName }}</span>
                    <button class="btn-auth" @click="logout">Выйти</button>
                </div>
            </div>
        </div>
    </header>

    <!-- Модальное окно входа -->
    <div v-if="showLoginModal" class="modal-overlay" @click.self="closeModals">
        <div class="modal-container">
            <div class="modal-header">
                <h2>Вход в аккаунт</h2>
                <button class="modal-close" @click="closeModals">&times;</button>
            </div>
            <div class="modal-body">
                <form @submit.prevent="handleLogin">
                    <div class="form-group">
                        <label>Телефон</label>
                        <input type="tel" v-model="loginForm.phone" placeholder="89991234567" required>
                    </div>
                    <div class="form-group">
                        <label>Пароль</label>
                        <input type="password" v-model="loginForm.password" placeholder="••••••••" required>
                    </div>
                    <div v-if="loginError" class="error-message">{{ loginError }}</div>
                    <button type="submit" class="btn-submit" :disabled="loading">
                        {{ loading ? 'Вход...' : 'Войти' }}
                    </button>
                    <p class="auth-switch">
                        Нет аккаунта? 
                        <a href="#" @click.prevent="switchToRegister">Зарегистрироваться</a>
                    </p>
                </form>
            </div>
        </div>
    </div>

    <!-- Модальное окно регистрации -->
    <div v-if="showRegisterModal" class="modal-overlay" @click.self="closeModals">
        <div class="modal-container">
            <div class="modal-header">
                <h2>Регистрация</h2>
                <button class="modal-close" @click="closeModals">&times;</button>
            </div>
            <div class="modal-body">
                <form @submit.prevent="handleRegister">
                    <div class="form-group">
                        <label>Имя</label>
                        <input type="text" v-model="registerForm.name" required>
                    </div>
                    <div class="form-group">
                        <label>Номер телефона</label>
                        <input type="tel" v-model="registerForm.phone" placeholder="89991234567" required>
                    </div>
                    <div class="form-group">
                        <label>Пароль</label>
                        <input type="password" v-model="registerForm.password" required>
                    </div>
                    <div v-if="registerError" class="error-message">{{ registerError }}</div>
                    <button type="submit" class="btn-submit" :disabled="loading">
                        {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
                    </button>
                    <p class="auth-switch">
                        Уже есть аккаунт? 
                        <a href="#" @click.prevent="switchToLogin">Войти</a>
                    </p>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
import { cinemaApi } from '../api/cinemaApi'

export default {
    name: 'Navbar',
    data() {
        return {
            showLoginModal: false,
            showRegisterModal: false,
            isAuthenticated: false,
            userName: '',
            isAdmin: false,
            loading: false,
            loginError: '',
            registerError: '',
            loginForm: { phone: '', password: '' },
            registerForm: { name: '', phone: '', password: '' }
        }
    },
    mounted() {
        this.checkAuth();
    },
    methods: {
        checkAuth() {
            const token = localStorage.getItem('auth_token');
            const user = localStorage.getItem('user_data');
            
            if (token && user) {
                this.isAuthenticated = true;
                const userData = JSON.parse(user);
                this.userName = userData.name;
                this.isAdmin = userData.role === 'Админ';
            }
        },
        async handleLogin() {
            this.loginError = '';
            this.loading = true;
            try {
                const data = await cinemaApi.login(this.loginForm.phone, this.loginForm.password);
                this.isAuthenticated = true;
                this.userName = data.user.name;
                this.isAdmin = data.user.role === 'Админ';
                this.closeModals();
                this.loginForm = { phone: '', password: '' };
                this.$emit('user-logged-in', data.user);
                window.location.reload();
            } catch (error) {
                this.loginError = error.message;
            } finally {
                this.loading = false;
            }
        },
        async handleRegister() {
            this.registerError = '';
            this.loading = true;
            try {
                const data = await cinemaApi.register({
                    name: this.registerForm.name,
                    phone: this.registerForm.phone,
                    password: this.registerForm.password
                });
                this.isAuthenticated = true;
                this.userName = data.user.name;
                this.isAdmin = false;
                this.closeModals();
                this.registerForm = { name: '', phone: '', password: '' };
                this.$emit('user-registered', data.user);
                window.location.reload();
            } catch (error) {
                this.registerError = error.message;
            } finally {
                this.loading = false;
            }
        },
        logout() {
            cinemaApi.logout();
            this.isAuthenticated = false;
            this.userName = '';
            this.isAdmin = false;
            this.$emit('user-logged-out');
            window.location.reload();
        },
        closeModals() {
            this.showLoginModal = false;
            this.showRegisterModal = false;
            this.loginError = '';
            this.registerError = '';
            this.loginForm = { phone: '', password: '' };
            this.registerForm = { name: '', phone: '', password: '' };
        },
        switchToRegister() {
            this.showLoginModal = false;
            this.showRegisterModal = true;
        },
        switchToLogin() {
            this.showRegisterModal = false;
            this.showLoginModal = true;
        }
    }
}
</script>

<style scoped>
.navbar {
    background: rgba(18, 18, 24, 0.96);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid #2a2a2e;
    position: sticky;
    top: 0;
    z-index: 100;
    width: 100%;
}

.container {
    max-width: 1280px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 24px;
}

.logo a {
    font-size: 1.8rem;
    font-weight: 700;
    color: #f5c518;
    text-decoration: none;
}

.nav-links {
    display: flex;
    gap: 2rem;
}

.nav-link {
    color: #e2e2e8;
    text-decoration: none;
    font-weight: 500;
    transition: 0.2s;
    padding: 0.5rem 0;
    border-bottom: 2px solid transparent;
}

.nav-link:hover, 
.nav-link.router-link-active {
    color: #f5c518;
    border-bottom-color: #f5c518;
}

.btn-auth {
    background: #2c2c34;
    border: none;
    padding: 0.6rem 1.4rem;
    border-radius: 40px;
    font-weight: 600;
    color: white;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.9rem;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.btn-auth:hover {
    background: #f5c518;
    color: #121212;
}

.user-menu {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.user-name {
    color: #e2e2e8;
    font-weight: 500;
}

.admin-badge {
    background: #f5c518;
    color: #121212;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
}

/* Модальные окна - центрированные */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-container {
    background: #1e1e24;
    border-radius: 16px;
    width: 90%;
    max-width: 450px;
    border: 1px solid #2a2a2e;
    animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: scale(0.95);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

.modal-header {
    padding: 20px 24px;
    border-bottom: 1px solid #2a2a2e;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h2 {
    margin: 0;
    color: #f5c518;
    font-size: 1.3rem;
}

.modal-close {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #888;
    transition: 0.2s;
}

.modal-close:hover {
    color: #f5c518;
}

.modal-body {
    padding: 24px;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    color: #e2e2e8;
    font-weight: 500;
}

.form-group input {
    width: 100%;
    padding: 12px;
    background: #2c2c34;
    border: 1px solid #3a3a42;
    border-radius: 8px;
    color: white;
    font-size: 1rem;
}

.form-group input:focus {
    outline: none;
    border-color: #f5c518;
}

.btn-submit {
    width: 100%;
    padding: 12px;
    background: #f5c518;
    color: #121212;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: 0.2s;
}

.btn-submit:hover:not(:disabled) {
    background: #e0b414;
}

.btn-submit:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.error-message {
    background: rgba(220, 38, 38, 0.1);
    border: 1px solid #dc2626;
    color: #dc2626;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 15px;
    font-size: 0.9rem;
    text-align: center;
}

.auth-switch {
    text-align: center;
    margin-top: 20px;
    color: #888;
}

.auth-switch a {
    color: #f5c518;
    text-decoration: none;
}

@media (max-width: 768px) {
    .container {
        flex-direction: column;
        gap: 1rem;
    }
    .nav-links {
        gap: 1rem;
        flex-wrap: wrap;
        justify-content: center;
    }
}
</style>