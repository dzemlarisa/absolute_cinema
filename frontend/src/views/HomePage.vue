<template>
    <div class="home-page">
        <section class="hero">
            <div class="container">
                <h1>Билеты в кино</h1>
                <p>Выбирайте фильмы, сеансы и места — всё за пару кликов</p>
            </div>
        </section>

        <section class="movies-preview">
            <div class="container">
                <h2>Сейчас в прокате</h2>
                <div v-if="loadingMovies" class="loading">
                    <i class="fas fa-spinner fa-pulse"></i> Загрузка фильмов...
                </div>
                <div v-else-if="movies.length === 0" class="no-results">
                    <i class="fas fa-film"></i>
                    <p>Фильмы не найдены</p>
                </div>
                <div v-else class="movies-grid">
                    <div v-for="movie in movies.slice(0, 4)" :key="movie.id" class="movie-card">

                        <div class="movie-info">
                            <h3>{{ movie.name }}</h3>
                            <div class="movie-meta">
                                <span><i class="fas fa-clock"></i> {{ movie.time }}</span>
                                <span><i class="fas fa-tag"></i> {{ movie.genre }}</span>
                            </div>
                            <button class="btn-buy" @click="buyTicket(movie.id)">Купить билет</button>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section class="features">
            <div class="container">
                <div class="features-grid">
                    <div class="feature-item">
                        <i class="fas fa-ticket-alt"></i>
                        <h3>Без комиссии</h3>
                        <p>Цена билета как в кассе кинотеатра</p>
                    </div>
                    <div class="feature-item">
                        <i class="fas fa-headset"></i>
                        <h3>Поддержка 24/7</h3>
                        <p>Поможем с любым вопросом</p>
                    </div>
                </div>
            </div>
        </section>
    </div>
</template>

<script>
import { cinemaApi } from '../api/cinemaApi'

export default {
    name: 'HomePage',
    data() {
        return {
            movies: [],
            loadingMovies: true
        }
    },
    async mounted() {
        await this.loadMovies()
    },
    methods: {
        async loadMovies() {
            try {
                this.movies = await cinemaApi.getMovies()
            } catch (error) {
                console.error('Ошибка загрузки фильмов:', error)
                this.movies = []
            } finally {
                this.loadingMovies = false
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
    padding: 4rem 0;
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

.movies-preview {
    padding: 4rem 0;
}

.container {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 24px;
}

.movies-preview h2 {
    text-align: center;
    margin-bottom: 2rem;
    font-size: 2rem;
}

.movies-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 2rem;
}

.movie-card {
    background: #18181e;
    border-radius: 24px;
    overflow: hidden;
    transition: transform 0.25s ease, box-shadow 0.25s;
    border: 1px solid #2c2c30;
}

.movie-card:hover {
    transform: translateY(-5px);
    border-color: #f5c518;
    box-shadow: 0 20px 30px -12px rgba(0, 0, 0, 0.5);
}

.movie-poster {
    position: relative;
    height: 340px;
    overflow: hidden;
}

.movie-poster img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s;
}

.movie-card:hover .movie-poster img {
    transform: scale(1.05);
}

.rating {
    position: absolute;
    top: 12px;
    right: 12px;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(4px);
    padding: 4px 10px;
    border-radius: 30px;
    font-weight: 700;
    color: #f5c518;
    font-size: 0.9rem;
}

.movie-info {
    padding: 1.2rem;
}

.movie-info h3 {
    margin-bottom: 0.5rem;
    font-size: 1.2rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.movie-meta {
    display: flex;
    gap: 0.8rem;
    font-size: 0.75rem;
    color: #a1a1aa;
    margin-bottom: 1rem;
}

.movie-meta i {
    margin-right: 4px;
}

.btn-buy {
    background: #f5c518;
    border: none;
    width: 100%;
    padding: 0.75rem;
    border-radius: 40px;
    font-weight: 700;
    font-size: 0.9rem;
    cursor: pointer;
    transition: 0.2s;
    color: #121212;
}

.btn-buy:hover {
    background: #ffda44;
    transform: scale(0.98);
    box-shadow: 0 4px 12px rgba(245, 197, 24, 0.3);
}

.features {
    padding: 4rem 0;
    background: #121216;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
    text-align: center;
}

.feature-item i {
    font-size: 2.5rem;
    color: #f5c518;
    margin-bottom: 1rem;
}

.feature-item h3 {
    margin-bottom: 0.5rem;
}

.feature-item p {
    color: #9f9faa;
    font-size: 0.9rem;
}

.loading, .no-results {
    text-align: center;
    padding: 3rem;
    color: #a1a1aa;
}

.loading i, .no-results i {
    font-size: 2rem;
    margin-bottom: 1rem;
    color: #f5c518;
}
</style>