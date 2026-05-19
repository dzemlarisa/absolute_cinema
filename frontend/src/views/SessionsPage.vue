<template>
    <div class="sessions-page">
        <section class="hero">
            <div class="container">
                <h1>Управление сеансами</h1>
                <button v-if="isAdmin" class="btn-create" @click="openCreateSessionModal">
                    + Создать сеанс
                </button>
            </div>
        </section>

        <section class="sessions-section">
            <div class="container">
                <div class="filters">
                    <select v-model="filters.movieId" class="filter-select" @change="loadSessions">
                        <option :value="null">Все фильмы</option>
                        <option v-for="movie in movies" :key="movie.id" :value="movie.id">
                            {{ movie.name }}
                        </option>
                    </select>
                    <select v-model="filters.cinemaId" class="filter-select" @change="loadSessions">
                        <option :value="null">Все кинотеатры</option>
                        <option v-for="cinema in cinemas" :key="cinema.id" :value="cinema.id">
                            {{ cinema.name }}
                        </option>
                    </select>
                </div>

                <div v-if="loading" class="loading">
                    <i class="fas fa-spinner fa-pulse"></i> Загрузка сеансов...
                </div>

                <div v-else-if="sessions.length === 0" class="no-results">  
                    <p>Сеансы не найдены</p>
                </div>

                <div v-else class="sessions-list">
                    <div v-for="session in sessions" :key="session.id" class="session-card">
                        <div class="session-info">
                            <h3>{{ getMovieName(session.movie_id) }}</h3>
                            <div class="session-details">
                                <span><i class="fas fa-building"></i> {{ getCinemaName(session.cinema_id) }}</span>
                                <span><i class="fas fa-door-open"></i> Зал: {{ getHallName(session.hall_id) }}</span>
                                <span><i class="fas fa-clock"></i> {{ formatTime(session.start_time) }}</span>
                                <span><i class="fas fa-chair"></i> Свободно: {{ session.remaining_seats }}</span>
                            </div>
                            <button v-if="isAdmin" class="btn-delete" @click="deleteSession(session.id)">
                                <i class="fas fa-trash"></i> Удалить сеанс
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <div v-if="showSessionModal" class="modal-overlay" @click.self="closeSessionModal">
            <div class="modal-container">
                <div class="modal-header">
                    <h2>Создать сеанс</h2>
                    <button class="modal-close" @click="closeSessionModal">&times;</button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="createSession">
                        <div class="form-group">
                            <label>Фильм</label>
                            <select v-model="sessionForm.movie_id" class="form-select" required>
                                <option :value="null">Выберите фильм</option>
                                <option v-for="movie in movies" :key="movie.id" :value="movie.id">
                                    {{ movie.name }}
                                </option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Кинотеатр</label>
                            <select v-model="sessionForm.cinema_id" class="form-select" @change="onCinemaChange" required>
                                <option :value="null">Выберите кинотеатр</option>
                                <option v-for="cinema in cinemas" :key="cinema.id" :value="cinema.id">
                                    {{ cinema.name }}
                                </option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Зал</label>
                            <select v-model="sessionForm.hall_id" class="form-select" required>
                                <option :value="null">Выберите зал</option>
                                <option v-for="hall in availableHalls" :key="hall.id" :value="hall.id">
                                    {{ hall.name }} ({{ hall.capacity }} мест)
                                </option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Дата и время</label>
                            <input type="datetime-local" v-model="sessionForm.start_time" class="form-input" required>
                        </div>
                        <div v-if="modalError" class="error-message">{{ modalError }}</div>
                        <div class="modal-actions">
                            <button type="button" class="btn-cancel" @click="closeSessionModal">Отмена</button>
                            <button type="submit" class="btn-submit" :disabled="modalLoading">
                                {{ modalLoading ? 'Создание...' : 'Создать сеанс' }}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { cinemaApi } from '../api/cinemaApi'

export default {
    name: 'SessionsPage',
    data() {
        return {
            sessions: [],
            movies: [],
            cinemas: [],
            halls: {},
            loading: true,
            isAdmin: false,
            filters: {
                movieId: null,
                cinemaId: null
            },
            showSessionModal: false,
            sessionForm: {
                movie_id: null,
                cinema_id: null,
                hall_id: null,
                start_time: ''
            },
            availableHalls: [],
            modalLoading: false,
            modalError: ''
        }
    },
    mounted() {
        this.checkAdminStatus();
        this.loadMovies();
        this.loadCinemas();
        this.loadSessions();
    },
    methods: {
        checkAdminStatus() {
            const user = localStorage.getItem('user_data');
            if (user) {
                try {
                    const userData = JSON.parse(user);
                    this.isAdmin = userData.role === 'Админ';
                    if (!this.isAdmin) {
                        this.$router.push('/');
                    }
                } catch(e) {
                    this.isAdmin = false;
                }
            }
        },
        async loadMovies() {
            try {
                this.movies = await cinemaApi.getMovies();
            } catch (error) {
                console.error('Ошибка загрузки фильмов:', error);
            }
        },
        async loadCinemas() {
            try {
                this.cinemas = await cinemaApi.getCinemas();
                for (const cinema of this.cinemas) {
                    this.halls[cinema.id] = await cinemaApi.getCinemaHalls(cinema.id);
                }
            } catch (error) {
                console.error('Ошибка загрузки кинотеатров:', error);
            }
        },
        async loadSessions() {
            this.loading = true;
            try {
                const params = {};
                if (this.filters.movieId) params.movie_id = this.filters.movieId;
                if (this.filters.cinemaId) params.cinema_id = this.filters.cinemaId;
                this.sessions = await cinemaApi.getSessions(params);
            } catch (error) {
                console.error('Ошибка загрузки сеансов:', error);
                this.sessions = [];
            } finally {
                this.loading = false;
            }
        },
        getMovieName(movieId) {
            const movie = this.movies.find(m => m.id === movieId);
            return movie ? movie.name : 'Неизвестный фильм';
        },
        getCinemaName(cinemaId) {
            const cinema = this.cinemas.find(c => c.id === cinemaId);
            return cinema ? cinema.name : 'Неизвестный кинотеатр';
        },
        getHallName(hallId) {
            for (const cinema of this.cinemas) {
                const hall = this.halls[cinema.id]?.find(h => h.id === hallId);
                if (hall) return hall.name;
            }
            return 'Неизвестный зал';
        },
        formatTime(dateTime) {
            if (!dateTime) return '';
            const date = new Date(dateTime);
            return date.toLocaleString('ru-RU', {
                day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'
            });
        },
        onCinemaChange() {
            this.sessionForm.hall_id = null;
            this.availableHalls = this.halls[this.sessionForm.cinema_id] || [];
        },
        openCreateSessionModal() {
            this.sessionForm = {
                movie_id: null,
                cinema_id: null,
                hall_id: null,
                start_time: ''
            };
            this.availableHalls = [];
            this.showSessionModal = true;
        },
        closeSessionModal() {
            this.showSessionModal = false;
            this.modalError = '';
        },
        async createSession() {
            if (!this.sessionForm.movie_id || !this.sessionForm.cinema_id || !this.sessionForm.hall_id || !this.sessionForm.start_time) {
                this.modalError = 'Заполните все поля';
                return;
            }
            
            this.modalLoading = true;
            this.modalError = '';
            
            try {
                const startTime = new Date(this.sessionForm.start_time);
                const movie = this.movies.find(m => m.id === this.sessionForm.movie_id);
                const duration = parseInt(movie.time) || 120;
                const endTime = new Date(startTime.getTime() + duration * 60000);
                
                await cinemaApi.createSession({
                    movie_id: this.sessionForm.movie_id,
                    cinema_id: this.sessionForm.cinema_id,
                    hall_id: this.sessionForm.hall_id,
                    start_time: startTime.toISOString(),
                    end_time: endTime.toISOString(),
                    remaining_seats: this.availableHalls.find(h => h.id === this.sessionForm.hall_id)?.capacity || 0
                });
                
                this.closeSessionModal();
                await this.loadSessions();
            } catch (error) {
                this.modalError = error.message || 'Ошибка создания сеанса';
            } finally {
                this.modalLoading = false;
            }
        },
        async deleteSession(sessionId) {
            if (confirm('Вы уверены, что хотите удалить этот сеанс? Все связанные билеты будут удалены.')) {
                try {
                    await cinemaApi.deleteSession(sessionId);
                    await this.loadSessions();
                } catch (error) {
                    alert('Ошибка при удалении сеанса');
                }
            }
        }
    }
}
</script>

<style scoped>
.hero {
    background: linear-gradient(135deg, #1e1e2a 0%, #0b0b10 100%);
    padding: 3rem 0;
    text-align: center;
}

.hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.hero p {
    font-size: 1.2rem;
    color: #b9b9c3;
}

.btn-create {
    background: #f5c518;
    border: none;
    padding: 0.6rem 1.5rem;
    border-radius: 40px;
    font-weight: 600;
    cursor: pointer;
    margin-top: 1rem;
}

.sessions-section {
    padding: 3rem 0;
}

.container {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 24px;
}

.filters {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
    justify-content: center;
}

.filter-select {
    padding: 0.6rem 1.5rem;
    background: #2c2c34;
    border: 1px solid #3a3a42;
    border-radius: 40px;
    color: white;
    cursor: pointer;
}

.sessions-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.session-card {
    background: #18181e;
    border-radius: 16px;
    border: 1px solid #2c2c30;
    padding: 1.2rem;
    transition: transform 0.2s;
}

.session-card:hover {
    border-color: #f5c518;
}

.session-info h3 {
    color: #f5c518;
    margin-bottom: 0.5rem;
}

.session-details {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    font-size: 0.85rem;
    color: #a1a1aa;
    margin: 0.8rem 0;
}

.session-details i {
    margin-right: 4px;
    color: #f5c518;
}

.btn-delete {
    background: #dc2626;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 40px;
    font-weight: 600;
    cursor: pointer;
    color: white;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.btn-delete:hover {
    background: #ef4444;
}

.loading, .no-results {
    text-align: center;
    padding: 3rem;
    color: #a1a1aa;
}

.no-results i {
    font-size: 3rem;
    margin-bottom: 1rem;
    color: #f5c518;
}

/* Модальное окно */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.85);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-container {
    background: #1e1e24;
    border-radius: 24px;
    width: 90%;
    max-width: 450px;
    border: 1px solid rgba(245, 197, 24, 0.3);
    animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}

.modal-header {
    padding: 1.5rem;
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
}

.modal-close:hover {
    color: #f5c518;
}

.modal-body {
    padding: 1.5rem;
}

.form-group {
    margin-bottom: 1rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: #e2e2e8;
    font-weight: 500;
}

.form-select, .form-input {
    width: 100%;
    padding: 10px 14px;
    background: #2c2c34;
    border: 1px solid #3a3a42;
    border-radius: 10px;
    color: white;
    font-size: 0.9rem;
}

.form-select:focus, .form-input:focus {
    outline: none;
    border-color: #f5c518;
}

.modal-actions {
    display: flex;
    gap: 1rem;
    margin-top: 1.5rem;
}

.btn-cancel {
    flex: 1;
    padding: 10px;
    background: #2c2c34;
    border: 1px solid #3a3a42;
    border-radius: 40px;
    color: white;
    cursor: pointer;
}

.btn-cancel:hover {
    background: #3a3a42;
}

.btn-submit {
    flex: 2;
    padding: 10px;
    background: #f5c518;
    border: none;
    border-radius: 40px;
    font-weight: 600;
    cursor: pointer;
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
    border-radius: 10px;
    margin-bottom: 1rem;
    font-size: 0.85rem;
    text-align: center;
}

@media (max-width: 768px) {
    .filters {
        flex-direction: column;
    }
    .hero h1 {
        font-size: 2rem;
    }
}
</style>