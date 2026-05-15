<template>
    <div class="ticket-page">
        <section class="hero">
            <div class="container">
                <h1>Купить билет</h1>
                <p>Выберите фильм, кинотеатр и сеанс</p>
            </div>
        </section>

        <section class="booking-section">
            <div class="container">
                <!-- Шаг 1: Выбор фильма -->
                <div class="step" v-if="step === 1">
                    <h2>Шаг 1: Выберите фильм</h2>
                    <div class="movies-list" v-if="!loadingMovies">
                        <div v-for="movie in movies" :key="movie.id" 
                             :class="['movie-option', { selected: selectedMovie?.id === movie.id }]"
                             @click="selectMovie(movie)">
                            <img :src="movie.poster || 'https://via.placeholder.com/80x120'" :alt="movie.name">
                            <div class="movie-option-info">
                                <h3>{{ movie.name }}</h3>
                                <p>{{ movie.genre }} • {{ movie.time }}</p>
                                <p class="price">{{ movie.price }} ₽</p>
                            </div>
                        </div>
                    </div>
                    <div v-else class="loading">Загрузка фильмов...</div>
                </div>

                <!-- Шаг 2: Выбор кинотеатра -->
                <div class="step" v-if="step === 2">
                    <button class="back-btn" @click="step = 1">← Назад</button>
                    <h2>Шаг 2: Выберите кинотеатр</h2>
                    <div class="cinemas-list">
                        <div v-for="cinema in cinemas" :key="cinema.id"
                             :class="['cinema-option', { selected: selectedCinema?.id === cinema.id }]"
                             @click="selectCinema(cinema)">
                            <i class="fas fa-building"></i>
                            <div>
                                <h3>{{ cinema.name }}</h3>
                                <p>{{ cinema.address }}</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Шаг 3: Выбор сеанса -->
                <div class="step" v-if="step === 3">
                    <button class="back-btn" @click="step = 2">← Назад</button>
                    <h2>Шаг 3: Выберите сеанс</h2>
                    <div v-if="loadingSessions" class="loading">Загрузка сеансов...</div>
                    <div v-else-if="sessions.length === 0" class="no-sessions">
                        Нет доступных сеансов для выбранного фильма и кинотеатра
                    </div>
                    <div class="sessions-list" v-else>
                        <div v-for="session in sessions" :key="session.id"
                             :class="['session-option', { selected: selectedSession?.id === session.id }]"
                             @click="selectSession(session)">
                            <div class="session-time">
                                <i class="fas fa-clock"></i>
                                {{ formatTime(session.start_time) }}
                            </div>
                            <div class="session-info">
                                <span>Зал: {{ session.hall_id }}</span>
                                <span>Свободно мест: {{ session.remaining_seats }}</span>
                            </div>
                            <div class="session-price">
                                {{ selectedMovie?.price }} ₽
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Шаг 4: Выбор количества билетов и оплата -->
                <div class="step" v-if="step === 4">
                    <button class="back-btn" @click="step = 3">← Назад</button>
                    <h2>Шаг 4: Оформление билетов</h2>
                    <div class="order-summary">
                        <h3>Ваш заказ</h3>
                        <div class="summary-item">
                            <span>Фильм:</span>
                            <strong>{{ selectedMovie?.name }}</strong>
                        </div>
                        <div class="summary-item">
                            <span>Кинотеатр:</span>
                            <strong>{{ selectedCinema?.name }}</strong>
                        </div>
                        <div class="summary-item">
                            <span>Время сеанса:</span>
                            <strong>{{ formatTime(selectedSession?.start_time) }}</strong>
                        </div>
                        <div class="summary-item">
                            <span>Цена билета:</span>
                            <strong>{{ selectedMovie?.price }} ₽</strong>
                        </div>
                        <div class="summary-item">
                            <span>Количество билетов:</span>
                            <div class="ticket-count">
                                <button @click="ticketCount = Math.max(1, ticketCount - 1)">-</button>
                                <span>{{ ticketCount }}</span>
                                <button @click="ticketCount = Math.min(selectedSession?.remaining_seats || 10, ticketCount + 1)">+</button>
                            </div>
                        </div>
                        <div class="summary-item total">
                            <span>Итого:</span>
                            <strong>{{ (selectedMovie?.price || 0) * ticketCount }} ₽</strong>
                        </div>
                        <button class="btn-pay" @click="payTicket" :disabled="paying">
                            {{ paying ? 'Оформление...' : 'Оплатить' }}
                        </button>
                    </div>
                </div>

                <!-- Успешная покупка -->
                <div class="step" v-if="step === 5">
                    <div class="success-message">
                        <i class="fas fa-check-circle"></i>
                        <h2>Билет успешно приобретён!</h2>
                        <p>Чек отправлен на вашу почту</p>
                        <button class="btn-new" @click="resetBooking">Купить ещё билет</button>
                    </div>
                </div>
            </div>
        </section>
    </div>
</template>

<script>
import { cinemaApi } from '../api/cinemaApi'

export default {
    name: 'TicketPage',
    data() {
        return {
            step: 1,
            movies: [],
            cinemas: [],
            sessions: [],
            selectedMovie: null,
            selectedCinema: null,
            selectedSession: null,
            ticketCount: 1,
            loadingMovies: true,
            loadingSessions: false,
            paying: false
        }
    },
    async mounted() {
        await this.loadMovies()
        await this.loadCinemas()
        
        // Если перешли с параметрами
        const movieId = this.$route.query.movieId
        if (movieId) {
            this.selectedMovie = this.movies.find(m => m.id == movieId)
            if (this.selectedMovie) this.step = 2
        }
        
        const cinemaId = this.$route.query.cinemaId
        if (cinemaId) {
            this.selectedCinema = this.cinemas.find(c => c.id == cinemaId)
            if (this.selectedCinema && this.selectedMovie) this.step = 3
        }
    },
    methods: {
        async loadMovies() {
            try {
                this.movies = await cinemaApi.getMovies()
                this.loadingMovies = false
            } catch (error) {
                console.error('Ошибка:', error)
                this.loadingMovies = false
            }
        },
        async loadCinemas() {
            try {
                this.cinemas = await cinemaApi.getCinemas()
            } catch (error) {
                console.error('Ошибка загрузки кинотеатров:', error)
            }
        },
        selectMovie(movie) {
            this.selectedMovie = movie
            this.step = 2
        },
        selectCinema(cinema) {
            this.selectedCinema = cinema
            this.loadSessions()
            this.step = 3
        },
        async loadSessions() {
            this.loadingSessions = true
            try {
                this.sessions = await cinemaApi.getSessions({
                    movie_id: this.selectedMovie.id,
                    cinema_id: this.selectedCinema.id
                })
            } catch (error) {
                console.error('Ошибка загрузки сеансов:', error)
                this.sessions = []
            }
            this.loadingSessions = false
        },
        selectSession(session) {
            this.selectedSession = session
            this.ticketCount = 1
            this.step = 4
        },
        formatTime(dateTime) {
            if (!dateTime) return ''
            const date = new Date(dateTime)
            return date.toLocaleString('ru-RU', {
                day: '2-digit', month: '2-digit',
                hour: '2-digit', minute: '2-digit'
            })
        },
        async payTicket() {
            this.paying = true
            try {
                await cinemaApi.createTicket({
                    session_id: this.selectedSession.id,
                    ticket_cnt: this.ticketCount
                })
                this.step = 5
            } catch (error) {
                alert('Ошибка при покупке билета: ' + error.message)
            } finally {
                this.paying = false
            }
        },
        resetBooking() {
            this.step = 1
            this.selectedMovie = null
            this.selectedCinema = null
            this.selectedSession = null
            this.ticketCount = 1
        }
    }
}
</script>

<style scoped>
.hero {
    background: linear-gradient(135deg, #1e1e2a 0%, #0b0b10 100%);
    padding: 2rem 0;
    text-align: center;
}

.booking-section {
    padding: 2rem 0 4rem;
}

.container {
    max-width: 900px;
    margin: 0 auto;
    padding: 0 24px;
}

.step {
    background: #18181e;
    border-radius: 24px;
    padding: 2rem;
}

.step h2 {
    margin-bottom: 1.5rem;
    color: #f5c518;
}

.back-btn {
    background: transparent;
    border: 1px solid #f5c518;
    color: #f5c518;
    padding: 0.5rem 1rem;
    border-radius: 40px;
    cursor: pointer;
    margin-bottom: 1rem;
}

.movies-list, .cinemas-list, .sessions-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.movie-option, .cinema-option, .session-option {
    display: flex;
    gap: 1rem;
    padding: 1rem;
    background: #25252b;
    border-radius: 16px;
    cursor: pointer;
    transition: all 0.2s;
    border: 2px solid transparent;
}

.movie-option:hover, .cinema-option:hover, .session-option:hover {
    background: #2f2f36;
}

.movie-option.selected, .cinema-option.selected, .session-option.selected {
    border-color: #f5c518;
    background: #2f2f36;
}

.movie-option img {
    width: 60px;
    height: 90px;
    object-fit: cover;
    border-radius: 8px;
}

.movie-option-info h3 {
    margin-bottom: 0.3rem;
}

.price {
    color: #f5c518;
    font-weight: bold;
    margin-top: 0.3rem;
}

.session-time {
    font-size: 1.2rem;
    font-weight: bold;
    min-width: 100px;
}

.session-info {
    flex: 1;
    display: flex;
    gap: 1rem;
}

.session-price {
    font-weight: bold;
    color: #f5c518;
}

.order-summary {
    background: #25252b;
    border-radius: 16px;
    padding: 1.5rem;
}

.summary-item {
    display: flex;
    justify-content: space-between;
    padding: 0.8rem 0;
    border-bottom: 1px solid #3a3a42;
}

.summary-item.total {
    font-size: 1.2rem;
    font-weight: bold;
    border-bottom: none;
}

.ticket-count {
    display: flex;
    gap: 1rem;
    align-items: center;
}

.ticket-count button {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    border: none;
    background: #f5c518;
    font-size: 1.2rem;
    cursor: pointer;
}

.btn-pay {
    width: 100%;
    padding: 1rem;
    background: #f5c518;
    border: none;
    border-radius: 40px;
    font-weight: bold;
    font-size: 1.1rem;
    margin-top: 1.5rem;
    cursor: pointer;
}

.btn-pay:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.success-message {
    text-align: center;
    padding: 2rem;
}

.success-message i {
    font-size: 4rem;
    color: #4caf50;
    margin-bottom: 1rem;
}

.btn-new {
    background: #f5c518;
    border: none;
    padding: 0.8rem 2rem;
    border-radius: 40px;
    font-weight: bold;
    margin-top: 1.5rem;
    cursor: pointer;
}

.loading, .no-sessions {
    text-align: center;
    padding: 2rem;
    color: #a1a1aa;
}
</style>