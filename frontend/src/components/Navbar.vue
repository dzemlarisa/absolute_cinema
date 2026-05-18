//navbar
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
                <router-link to="/ticket" class="nav-link">Купить билет</router-link>
            </nav>
            <div class="auth-buttons">
                <button v-if="!isAuthenticated" class="btn-auth" @click="showLoginModal = true">Вход</button>
                <div v-else class="user-menu">
                    <span class="user-name">{{ userName }}</span>
                    <button class="btn-auth" @click="logout">Выйти</button>
                </div>
            </div>
        </div>
    </header>

    <div v-if="showLoginModal" class="modal" @click.self="closeModals">
            <div class="modal-content">
                <span class="close-modal" @click="closeModals">&times;</span>
                <div class="modal-header">
                    <h2>Вход в аккаунт</h2>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="handleLogin">
                        <div class="form-group">
                            <label>Телефон</label>
                            <input 
                                type="tel" 
                                v-model="loginForm.phone"
                                required 
                                placeholder="89991234567"
                            >
                        </div>
                        <div class="form-group">
                            <label>Пароль</label>
                            <input 
                                type="password" 
                                v-model="loginForm.password"
                                placeholder="••••••••" 
                                required
                            >
                        </div>
                        <div v-if="loginError" class="error-message">{{ loginError }}</div>
                        <button type="submit" class="btn-auth-submit" :disabled="loading">
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

        <div v-if="showRegisterModal" class="modal" @click.self="closeModals">
            <div class="modal-content">
                <span class="close-modal" @click="closeModals">&times;</span>
                <div class="modal-header">
                    <h2>Регистрация</h2>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="handleRegister">
                        <div class="form-group">
                            <label>Имя</label>
                            <input 
                                type="text" 
                                v-model="registerForm.name"
                                required
                            >
                        </div>
                        <div class="form-group">
                            <label>Номер телефона</label>
                            <input 
                                type="tel" 
                                v-model="registerForm.phone"
                                required 
                                placeholder="89991234567"
                            >
                        </div>
                        <div class="form-group">
                            <label>Пароль</label>
                            <input 
                                type="password" 
                                v-model="registerForm.password"
                                required 
                            >
                        </div>
                        <div v-if="registerError" class="error-message">{{ registerError }}</div>
                        <button type="submit" class="btn-auth-submit" :disabled="loading">
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
const API_BASE_URL = 'http://localhost:8001';

export default {
    name: 'Navbar',
    data() {
        return {
            showLoginModal: false,
            showRegisterModal: false,
            isAuthenticated: false,
            userName: '',
            loading: false,
            loginError: '',
            registerError: '',
            loginForm: {
                phone: '',
                password: ''
            },
            registerForm: {
                name: '',
                phone: '',
                password: ''
            }
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
                this.userName = JSON.parse(user).name;
            }
        },
        
        async handleLogin() {
            this.loginError = '';
            this.loading = true;
            
            try {
                const response = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        phone: this.loginForm.phone,
                        password: this.loginForm.password
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // Сохраняем токен и данные пользователя
                    localStorage.setItem('auth_token', data.access_token);
                    localStorage.setItem('token_type', data.token_type);
                    localStorage.setItem('user_data', JSON.stringify(data.user));
                    
                    this.isAuthenticated = true;
                    this.userName = data.user.name;
                    this.closeModals();
                    this.loginForm = { phone: '', password: '' };
                    
                    this.$emit('user-logged-in', data.user);
                } else {
                    this.loginError = data.detail || 'Ошибка входа';
                }
            } catch (error) {
                console.error('Ошибка:', error);
                this.loginError = 'Не удалось соединиться с сервером';
            } finally {
                this.loading = false;
            }
        },
        
        async handleRegister() {
            this.registerError = '';
            this.loading = true;
            
            try {
                const response = await fetch(`${API_BASE_URL}/auth/register`, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        name: this.registerForm.name,
                        phone: this.registerForm.phone,
                        password: this.registerForm.password
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // Сохраняем токен и данные пользователя
                    localStorage.setItem('auth_token', data.access_token);
                    localStorage.setItem('token_type', data.token_type);
                    localStorage.setItem('user_data', JSON.stringify(data.user));
                    
                    this.isAuthenticated = true;
                    this.userName = data.user.name;
                    this.closeModals();
                    this.registerForm = {
                        name: '',
                        phone: '',
                        password: ''
                    };
                    
                    this.$emit('user-registered', data.user);
                } else if (response.status === 409) {
                    this.registerError = data.detail || 'Пользователь с таким номером уже существует';
                } else {
                    this.registerError = data.detail || 'Ошибка регистрации';
                }
            } catch (error) {
                console.error('Ошибка:', error);
                this.registerError = 'Не удалось соединиться с сервером';
            } finally {
                this.loading = false;
            }
        },
        
        logout() {
            localStorage.removeItem('auth_token');
            localStorage.removeItem('token_type');
            localStorage.removeItem('user_data');
            this.isAuthenticated = false;
            this.userName = '';
            this.$emit('user-logged-out');
        },
        
        closeModals() {
            this.showLoginModal = false;
            this.showRegisterModal = false;
            this.loginError = '';
            this.registerError = '';
            this.loginForm = { phone: '', password: '' };
            this.registerForm = {
                name: '',
                phone: '',
                password: ''
            };
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
    width: 100%;
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
    white-space: nowrap;
}

.nav-links {
    display: flex;
    gap: 2rem;
    margin-left: 2rem;
}

.nav-link {
    color: #e2e2e8;
    text-decoration: none;
    font-weight: 500;
    transition: 0.2s;
    padding: 0.5rem 0;
    border-bottom: 2px solid transparent;
    white-space: nowrap;
}

.nav-link:hover, 
.nav-link.router-link-active {
    color: #f5c518;
    border-bottom-color: #f5c518;
}

.auth-buttons {
    margin-left: auto;
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
    white-space: nowrap;
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
    color: #f5c518;
    font-weight: 500;
}

.modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.modal-content {
    background: #1e1e24;
    border-radius: 16px;
    width: 90%;
    max-width: 450px;
    position: relative;
    animation: slideIn 0.3s ease;
    border: 1px solid #2a2a2e;
}

@keyframes slideIn {
    from {
        transform: translateY(-50px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.close-modal {
    position: absolute;
    right: 20px;
    top: 15px;
    font-size: 28px;
    cursor: pointer;
    color: #888;
    transition: 0.2s;
}

.close-modal:hover {
    color: #f5c518;
}

.modal-header {
    padding: 20px 24px;
    border-bottom: 1px solid #2a2a2e;
}

.modal-header h2 {
    margin: 0;
    color: #f5c518;
    font-size: 1.5rem;
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
    transition: 0.2s;
}

.form-group input:focus {
    outline: none;
    border-color: #f5c518;
}

.btn-auth-submit {
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

.btn-auth-submit:hover:not(:disabled) {
    background: #e0b414;
    transform: translateY(-1px);
}

.btn-auth-submit:disabled {
    opacity: 0.6;
    cursor: not-allowed;
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

.auth-switch a:hover {
    text-decoration: underline;
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

@media (max-width: 768px) {
    .container {
        flex-direction: column;
        gap: 1rem;
    }
    
    .auth-buttons {
        margin-left: 0;
    }
    
    .nav-links {
        margin-left: 0;
        gap: 1.5rem;
    }
}
</style>