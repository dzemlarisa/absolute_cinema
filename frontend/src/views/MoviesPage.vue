<template>
    <div class="movies-page">
        <section class="hero">
            <div class="container">
                <h1>Все фильмы</h1>
                <p>Выбирайте из актуального проката</p>
                <button v-if="isAdmin" class="btn-create" @click="openCreateMovieModal">
                    + Создать фильм
                </button>
            </div>
        </section>

        <section class="movies-section">
            <div class="container">
                <div class="filter-bar">
                    <div class="filter-buttons">
                        <button :class="['filter-btn', { active: currentFilter === 'all' }]" @click="currentFilter = 'all'">
                            Все жанры
                        </button>
                        <button v-for="genre in genres" :key="genre"
                            :class="['filter-btn', { active: currentFilter === genre }]" @click="currentFilter = genre">
                            {{ genre }}
                        </button>
                    </div>
                </div>

                <div v-if="loading" class="loading">
                    <i class="fas fa-spinner fa-pulse"></i> Загрузка фильмов...
                </div>

                <div v-else-if="filteredMovies.length === 0" class="no-results">
                    <i class="fas fa-film"></i>
                    <p>Фильмы не найдены</p>
                </div>

                <div v-else class="movies-grid">
                    <div v-for="movie in filteredMovies" :key="movie.id" class="movie-card">
                        <div class="movie-info">
                            <h3>{{ movie.name }}</h3>
                            <div class="movie-meta">
                                <span><i class="fas fa-clock"></i> {{ movie.time }} мин</span>
                                <span><i class="fas fa-tag"></i> {{ movie.genre }}</span>
                            </div>
                            <div class="movie-details">
                                <p><i class="fas fa-user"></i> <strong>Режиссёр:</strong> {{ movie.director }}</p>
                                <p v-if="movie.operator"><i class="fas fa-camera"></i> <strong>Оператор:</strong> {{ movie.operator }}</p>
                                <p><i class="fas fa-ruble-sign"></i> <strong>Цена:</strong> {{ movie.price }} ₽</p>
                            </div>
                            <div class="movie-actions">
                                <button class="btn-buy" @click="buyTicket(movie.id)">
                                    <i class="fas fa-ticket-alt"></i> Купить билет
                                </button>
                                <button v-if="isAdmin" class="btn-edit" @click="openEditMovieModal(movie)">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button v-if="isAdmin" class="btn-delete" @click="deleteMovie(movie.id)">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Модальное окно создания/редактирования фильма -->
        <div v-if="showMovieModal" class="modal-overlay" @click.self="closeMovieModal">
            <div class="modal-container modal-large">
                <div class="modal-header">
                    <h2>{{ isEditing ? 'Редактировать фильм' : 'Создать фильм' }}</h2>
                    <button class="modal-close" @click="closeMovieModal">&times;</button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="saveMovie">
                        <div class="form-row">
                            <div class="form-group">
                                <label>Название</label>
                                <input type="text" v-model="movieForm.name" required>
                            </div>
                            <div class="form-group">
                                <label>Жанр</label>
                                <input type="text" v-model="movieForm.genre" required>
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label>Режиссёр</label>
                                <input type="text" v-model="movieForm.director" required>
                            </div>
                            <div class="form-group">
                                <label>Оператор</label>
                                <input type="text" v-model="movieForm.operator">
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Актёры</label>
                            <input type="text" v-model="movieForm.actors">
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label>Студия</label>
                                <input type="text" v-model="movieForm.studio">
                            </div>
                            <div class="form-group">
                                <label>Продолжительность</label>
                                <input type="text" v-model="movieForm.time" placeholder="В минутах">
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Цена (₽)</label>
                            <input type="number" v-model="movieForm.price" required min="0">
                        </div>
                        <div v-if="modalError" class="error-message">{{ modalError }}</div>
                        <div class="modal-actions">
                            <button type="button" class="btn-cancel" @click="closeMovieModal">Отмена</button>
                            <button type="submit" class="btn-submit" :disabled="modalLoading">
                                {{ modalLoading ? 'Сохранение...' : (isEditing ? 'Сохранить' : 'Создать') }}
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
    name: 'MoviesPage',
    data() {
        return {
            movies: [],
            genres: [],
            loading: true,
            currentFilter: 'all',
            isAdmin: false,
            showMovieModal: false,
            isEditing: false,
            editingMovieId: null,
            movieForm: {
                name: '', director: '', operator: '', actors: '',
                genre: '', studio: '', time: '', price: 0
            },
            modalLoading: false,
            modalError: ''
        }
    },
    computed: {
        filteredMovies() {
            if (this.currentFilter === 'all') return this.movies
            return this.movies.filter(movie => movie.genre === this.currentFilter)
        }
    },
    mounted() {
        this.checkAdminStatus();
        this.loadMovies();
        this.loadGenres();
    },
    methods: {
        checkAdminStatus() {
            const user = localStorage.getItem('user_data');
            if (user) {
                try {
                    const userData = JSON.parse(user);
                    this.isAdmin = userData.role === 'Админ';
                } catch(e) {
                    this.isAdmin = false;
                }
            }
        },
        async loadMovies() {
            this.loading = true;
            try {
                this.movies = await cinemaApi.getMovies()
            } catch (error) {
                console.error('Ошибка загрузки фильмов:', error)
                this.movies = []
            } finally {
                this.loading = false
            }
        },
        async loadGenres() {
            try {
                this.genres = await cinemaApi.getGenres()
            } catch (error) {
                console.error('Ошибка загрузки жанров:', error)
                this.genres = []
            }
        },
        buyTicket(movieId) {
            this.$router.push({ name: 'ticket', query: { movieId } })
        },
        openCreateMovieModal() {
            this.isEditing = false;
            this.editingMovieId = null;
            this.movieForm = {
                name: '', director: '', operator: '', actors: '',
                genre: '', studio: '', time: '', price: 0
            };
            this.showMovieModal = true;
        },
        openEditMovieModal(movie) {
            this.isEditing = true;
            this.editingMovieId = movie.id;
            this.movieForm = {
                name: movie.name || '',
                director: movie.director || '',
                operator: movie.operator || '',
                actors: movie.actors || '',
                genre: movie.genre || '',
                studio: movie.studio || '',
                time: movie.time || '',
                price: movie.price || 0
            };
            this.showMovieModal = true;
        },
        closeMovieModal() {
            this.showMovieModal = false;
            this.modalError = '';
        },
        async saveMovie() {
            this.modalLoading = true;
            this.modalError = '';
            try {
                if (this.isEditing) {
                    await cinemaApi.updateMovie(this.editingMovieId, this.movieForm);
                } else {
                    await cinemaApi.createMovie(this.movieForm);
                }
                this.closeMovieModal();
                await this.loadMovies();
                await this.loadGenres();
            } catch (error) {
                this.modalError = error.message || 'Ошибка сохранения';
            } finally {
                this.modalLoading = false;
            }
        },
        async deleteMovie(movieId) {
            if (confirm('Вы уверены, что хотите удалить этот фильм? Все связанные сеансы также будут удалены.')) {
                try {
                    await cinemaApi.deleteMovie(movieId);
                    await this.loadMovies();
                    await this.loadGenres();
                } catch (error) {
                    alert('Ошибка при удалении фильма');
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

.movies-section {
    padding: 3rem 0;
}

.container {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 24px;
}

.filter-bar {
    margin-bottom: 2rem;
}

.filter-buttons {
    display: flex;
    gap: 0.8rem;
    flex-wrap: wrap;
    justify-content: center;
}

.filter-btn {
    background: #202028;
    border: none;
    padding: 0.6rem 1.5rem;
    border-radius: 40px;
    font-weight: 500;
    color: #dddddd;
    cursor: pointer;
    transition: all 0.2s;
}

.filter-btn:hover, .filter-btn.active {
    background: #f5c518;
    color: #0f0f12;
}

.movies-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 2rem;
}

.movie-card {
    background: #18181e;
    border-radius: 24px;
    transition: transform 0.25s ease;
    border: 1px solid #2c2c30;
}

.movie-card:hover {
    transform: translateY(-5px);
    border-color: #f5c518;
}

.movie-info {
    padding: 1.5rem;
}

.movie-info h3 {
    font-size: 1.3rem;
    margin-bottom: 0.5rem;
    color: #f5c518;
}

.movie-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.8rem;
    color: #a1a1aa;
    margin-bottom: 1rem;
}

.movie-meta i {
    margin-right: 4px;
}

.movie-details {
    font-size: 0.85rem;
    color: #b9b9c3;
    margin-bottom: 1rem;
}

.movie-details p {
    margin: 0.4rem 0;
}

.movie-details i {
    color: #f5c518;
    width: 20px;
}

.movie-actions {
    display: flex;
    gap: 0.5rem;
}

.btn-buy {
    background: #f5c518;
    border: none;
    flex: 2;
    padding: 0.7rem;
    border-radius: 40px;
    font-weight: 700;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.btn-buy:hover {
    background: #ffda44;
}

.btn-edit {
    background: #2c2c34;
    border: none;
    width: 40px;
    border-radius: 40px;
    cursor: pointer;
    color: #f5c518;
    display: flex;
    align-items: center;
    justify-content: center;
}

.btn-edit:hover {
    background: #f5c518;
    color: #121212;
}

.btn-delete {
    background: #dc2626;
    border: none;
    width: 40px;
    border-radius: 40px;
    cursor: pointer;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
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
    max-width: 500px;
    border: 1px solid rgba(245, 197, 24, 0.3);
    animation: fadeIn 0.2s ease;
}

.modal-large {
    max-width: 600px;
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

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.form-group {
    margin-bottom: 1rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: #e2e2e8;
    font-weight: 500;
    font-size: 0.85rem;
}

.form-group input {
    width: 100%;
    padding: 10px 14px;
    background: #2c2c34;
    border: 1px solid #3a3a42;
    border-radius: 10px;
    color: white;
    font-size: 0.9rem;
}

.form-group input:focus {
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
    .form-row {
        grid-template-columns: 1fr;
    }
    .movie-actions {
        flex-wrap: wrap;
    }
}
</style>