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
                <router-link v-if="isAdmin" to="/sessions" class="nav-link">Сеансы</router-link>
                <router-link to="/ticket" class="nav-link">Купить билет</router-link>
            </nav>
            <div class="auth-buttons">
                <button v-if="!isAuthenticated" class="btn-auth" @click="showLoginModal = true">Вход</button>
                <div v-else class="user-menu">
                    <span v-if="isAdmin" class="admin-badge">Администратор</span>
                    <span class="user-name" @click="toggleUserDropdown">
                        {{ userName }}
                        <i class="fas fa-chevron-down" :class="{ rotated: showUserDropdown }"></i>
                    </span>
                    <button class="btn-auth" @click="logout">Выйти</button>
                </div>
            </div>
        </div>

        <div v-if="showUserDropdown" class="dropdown-overlay" @click.self="closeUserDropdown">
            <div class="user-dropdown">
                <div class="dropdown-header">
                    <h3>Мои билеты</h3>
                    <button class="dropdown-close" @click="closeUserDropdown">&times;</button>
                </div>
                <div class="dropdown-body">
                    <div v-if="ticketsLoading" class="tickets-loading">
                        <i class="fas fa-spinner fa-pulse"></i> Загрузка билетов...
                    </div>
                    <div v-else-if="userTickets.length === 0" class="no-tickets">
                        <p>У вас пока нет билетов</p>
                        <router-link to="/ticket" class="buy-ticket-link" @click="closeUserDropdown">
                            Купить билет
                        </router-link>
                    </div>
                    <div v-else class="tickets-list">
                        <div v-for="ticket in userTickets" :key="ticket.id" class="ticket-item">
                            <div class="ticket-info">
                                <div class="ticket-movie">{{ getMovieName(ticket.session_id) }}</div>
                                <div class="ticket-details">
                                    <span>{{ getCinemaName(ticket.session_id) }}</span>
                                    <span>{{ getSessionTime(ticket.session_id) }}</span>
                                    <span>{{ ticket.ticket_cnt }} бил.</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </header>

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
            registerForm: { name: '', phone: '', password: '' },
            showUserDropdown: false,
            userTickets: [],
            ticketsLoading: false,
            sessionsCache: {}
        }
    },
    mounted() {
        this.checkAuth();
        document.addEventListener('click', this.handleClickOutside);
    },
    beforeDestroy() {
        document.removeEventListener('click', this.handleClickOutside);
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
        
        toggleUserDropdown() {
            if (!this.showUserDropdown) {
                this.loadUserTickets();
            }
            this.showUserDropdown = !this.showUserDropdown;
        },
        
        closeUserDropdown() {
            this.showUserDropdown = false;
        },
        
        handleClickOutside(event) {
            const dropdown = document.querySelector('.user-dropdown');
            const userName = document.querySelector('.user-name');
            if (dropdown && userName && 
                !dropdown.contains(event.target) && 
                !userName.contains(event.target)) {
                this.closeUserDropdown();
            }
        },
        
        async loadUserTickets() {
            this.ticketsLoading = true;
            try {
                const allTickets = await cinemaApi.getUserTickets();
                
                await this.loadSessionsInfo(allTickets);

                this.userTickets = allTickets.filter(ticket => {
                    const session = this.sessionsCache[ticket.session_id];
                    if (!session?.start_time) return false;
                    
                    const sessionTime = new Date(session.start_time);
                    const now = new Date();

                    return sessionTime > now;
                });
                
            } catch (error) {
                console.error('Ошибка загрузки билетов:', error);
                this.userTickets = [];
            } finally {
                this.ticketsLoading = false;
            }
        },
        
        async loadSessionsInfo(tickets = null) {
            const ticketsToUse = tickets || this.userTickets;
            const sessionIds = [...new Set(ticketsToUse.map(t => t.session_id))];
            
            for (const sessionId of sessionIds) {
                if (!this.sessionsCache[sessionId]) {
                    try {
                        // Получаем все сеансы или конкретный по ID
                        const sessions = await cinemaApi.getSessions();
                        const session = sessions.find(s => s.id === sessionId);
                        if (session) {
                            const movie = await cinemaApi.getMovie(session.movie_id);
                            const cinema = await cinemaApi.getCinema(session.cinema_id);
                            this.sessionsCache[sessionId] = {
                                ...session,
                                movie: movie,
                                cinema: cinema
                            };
                        }
                    } catch (error) {
                        console.error(`Ошибка загрузки сеанса ${sessionId}:`, error);
                    }
                }
            }
        },
        
        getMovieName(sessionId) {
            const session = this.sessionsCache[sessionId];
            return session?.movie?.name || 'Загрузка...';
        },
        
        getCinemaName(sessionId) {
            const session = this.sessionsCache[sessionId];
            return session?.cinema?.name || 'Загрузка...';
        },
        
        getSessionTime(sessionId) {
            const session = this.sessionsCache[sessionId];
            if (!session?.start_time) return 'Загрузка...';
            const date = new Date(session.start_time);
            return date.toLocaleString('ru-RU', {
                day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
            });
        },
        
        getTicketStatus(sessionId) {
            const session = this.sessionsCache[sessionId];
            if (!session?.start_time) return 'unknown';
            const sessionTime = new Date(session.start_time);
            const now = new Date();
            const threeHoursLater = new Date(sessionTime.getTime() - 3 * 60 * 60 * 1000);
            
            if (now > sessionTime) {
                return 'passed';
            } else if (now > threeHoursLater) {
                return 'soon';
            } else {
                return 'upcoming';
            }
        },
        
        getTicketStatusText(sessionId) {
            const status = this.getTicketStatus(sessionId);
            switch(status) {
                case 'passed': return 'Сеанс прошёл';
                case 'soon': return 'Скоро начнётся';
                case 'upcoming': return 'Предстоит';
                default: return 'Неизвестно';
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
.user-name {
    color: #e2e2e8;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: 0.2s;
    padding: 0.5rem 0;
}

.user-name:hover {
    color: #f5c518;
}

.user-name i {
    font-size: 0.8rem;
    transition: transform 0.2s;
}

.user-name i.rotated {
    transform: rotate(180deg);
}

.dropdown-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 999;
    display: flex;
    justify-content: flex-end;
    animation: fadeIn 0.2s ease;
}

.user-dropdown {
    position: fixed;
    top: 70px;
    right: 20px;
    width: 450px;
    max-width: calc(100vw - 40px);
    background: #1e1e24;
    border-radius: 16px;
    border: 1px solid #2a2a2e;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    z-index: 1000;
    animation: slideIn 0.2s ease;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.dropdown-header {
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #2a2a2e;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.dropdown-header h3 {
    margin: 0;
    color: #f5c518;
    font-size: 1.2rem;
}

.dropdown-close {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #888;
    transition: 0.2s;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.dropdown-close:hover {
    color: #f5c518;
}

.dropdown-body {
    max-height: 500px;
    overflow-y: auto;
    padding: 1rem;
}

.tickets-loading, .no-tickets {
    text-align: center;
    padding: 2rem;
    color: #a1a1aa;
}

.no-tickets i {
    font-size: 3rem;
    margin-bottom: 1rem;
    color: #f5c518;
}

.buy-ticket-link {
    display: inline-block;
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background: #f5c518;
    color: #121212;
    text-decoration: none;
    border-radius: 40px;
    font-weight: 600;
    transition: 0.2s;
}

.buy-ticket-link:hover {
    background: #e0b414;
}

.tickets-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.ticket-item {
    background: #2c2c34;
    border-radius: 12px;
    padding: 1rem;
    transition: 0.2s;
    border: 1px solid #3a3a42;
}

.ticket-item:hover {
    border-color: #f5c518;
    transform: translateX(-5px);
}

.ticket-movie {
    font-size: 1rem;
    font-weight: 600;
    color: #f5c518;
    margin-bottom: 0.5rem;
}

.ticket-details {
    display: flex;
    flex-wrap: wrap;
    gap: 0.8rem;
    font-size: 0.8rem;
    color: #a1a1aa;
    margin: 0.5rem 0;
}

.ticket-details i {
    color: #f5c518;
    margin-right: 4px;
}



.dropdown-body::-webkit-scrollbar {
    width: 8px;
}

.dropdown-body::-webkit-scrollbar-track {
    background: #2c2c34;
    border-radius: 4px;
}

.dropdown-body::-webkit-scrollbar-thumb {
    background: #f5c518;
    border-radius: 4px;
}

.dropdown-body::-webkit-scrollbar-thumb:hover {
    background: #e0b414;
}

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
        .user-dropdown {
        top: 60px;
        right: 10px;
        left: 10px;
        width: auto;
    }
    
    .ticket-details {
        flex-direction: column;
        gap: 0.3rem;
    }
    
    .user-name {
        font-size: 0.9rem;
    }
}

</style>