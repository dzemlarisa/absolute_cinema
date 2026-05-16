<template>
    <div class="movies-page">
        <section class="hero">
            <div class="container">
                <h1>Все фильмы</h1>
                <p>Выбирайте из актуального проката</p>
            </div>
        </section>

        <section class="movies-section">
            <div class="container">
                <div class="filter-bar">
                    <div class="filter-buttons">
                        <button 
                            :class="['filter-btn', { active: currentFilter === 'all' }]"
                            @click="currentFilter = 'all'"
                        >
                            Все жанры
                        </button>
                        <button 
                            v-for="genre in genres" 
                            :key="genre"
                            :class="['filter-btn', { active: currentFilter === genre }]"
                            @click="currentFilter = genre"
                        >
                            {{ genre }}
                        </button>
                    </div>
                </div>

                <div v-if="loading" class="loading">
                    <i class="fas fa-spinner fa-pulse"></i> Загрузка фильмов...
                </div>

                <div v-else-if="filteredMovies.length === 0" class="no-results">
                    <p>Фильмы не найдены</p>
                </div>

                <div v-else class="movies-grid">
                    <div v-for="movie in filteredMovies" :key="movie.id" class="movie-card">
                        <div class="movie-info">
                            <h3>{{ movie.name }}</h3>
                            <div class="movie-meta">
                                <span>{{ movie.time }} мин</span>
                                <span>{{ movie.genre }}</span>
                            </div>
                            <div class="movie-details">
                                <p><strong>Режиссёр:</strong> {{ movie.director }}</p>
                                <p v-if="movie.operator"><strong>Оператор:</strong> {{ movie.operator }}</p>
                                <p><strong>Цена:</strong> {{ movie.price }} ₽</p>
                            </div>
                            <button class="btn-buy" @click="buyTicket(movie.id)">
                                Купить билет
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </section>
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
            currentFilter: 'all'
        }
    },
    computed: {
        filteredMovies() {
            if (this.currentFilter === 'all') return this.movies
            return this.movies.filter(movie => movie.genre === this.currentFilter)
        }
    },
    async mounted() {
        await this.loadMovies()
        await this.loadGenres()
        this.loading = false
    },
    methods: {
        async loadMovies() {
            try {
                this.movies = await cinemaApi.getMovies()
            } catch (error) {
                console.error('Ошибка загрузки фильмов:', error)
                this.movies = []
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
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 2rem;
}

.movie-card {
    background: #18181e;
    border-radius: 24px;
    overflow: hidden;
    transition: transform 0.25s ease;
    border: 1px solid #2c2c30;
}

.movie-card:hover {
    transform: translateY(-5px);
    border-color: #f5c518;
}

.movie-poster {
    position: relative;
    height: 320px;
    overflow: hidden;
}

.movie-poster img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.rating {
    position: absolute;
    top: 12px;
    right: 12px;
    background: rgba(0,0,0,0.7);
    padding: 4px 10px;
    border-radius: 30px;
    font-weight: 700;
    color: #f5c518;
}

.movie-info {
    padding: 1.2rem;
}

.movie-info h3 {
    margin-bottom: 0.5rem;
    font-size: 1.2rem;
}

.movie-meta {
    display: flex;
    gap: 0.8rem;
    font-size: 0.8rem;
    color: #a1a1aa;
    margin-bottom: 0.8rem;
}

.movie-details {
    font-size: 0.85rem;
    color: #b9b9c3;
    margin-bottom: 1rem;
}

.movie-details p {
    margin: 0.3rem 0;
}

.btn-buy {
    background: #f5c518;
    border: none;
    width: 100%;
    padding: 0.7rem;
    border-radius: 40px;
    font-weight: 700;
    cursor: pointer;
    transition: 0.2s;
}

.btn-buy:hover {
    background: #ffda44;
    transform: scale(0.98);
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
</style>