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
                <h2>Новинки кино</h2>
                <div v-if="loadingMovies" class="loading">
                    <i class="fas fa-spinner fa-pulse"></i> Загрузка новинок...
                </div>
                <div v-else-if="newMovies.length === 0" class="no-results">
                    <p>Новинки не найдены</p>
                </div>
                <div v-else class="movies-grid">
                    <div v-for="movie in newMovies" :key="movie.id" class="movie-card">
                        <div class="movie-info">
                            <h3>{{ movie.name }}</h3>
                            <div class="movie-meta">
                                <span>{{ movie.time }} мин</span>
                                <span>{{ movie.genre }}</span>
                            </div>
                            <button class="btn-buy" @click="buyTicket(movie.id)">Купить билет</button>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section class="about-section">
            <div class="container">
                <div class="about-content">
                    <h2>О нас</h2>
                    <div class="about-grid">
                        <div class="about-card">
                            <h3>Список фильмов</h3>
                            <p>Просматривайте актуальную программу кинотеатров, изучайте описания, жанры и продолжительность фильмов.</p>
                        </div>
                        <div class="about-card">
                            <h3>Кинотеатры города</h3>
                            <p>Узнавайте адреса, контакты и расписание сеансов всех кинотеатров вашего города.</p>
                        </div>
                        <div class="about-card">
                            <h3>Покупка билетов</h3>
                            <p>Выбирайте удобные места, бронируйте и оплачивайте билеты онлайн без комиссии.</p>
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
    name: 'HomePage',
    data() {
        return {
            movies: [],
            loadingMovies: true
        }
    },
    computed: {
        // Берем последние 3 фильма (новинки) на основе id или даты добавления
        newMovies() {
            // Предполагаем, что фильмы приходят с сервера отсортированными по дате добавления
            // Если нет, сортируем по id в обратном порядке (новые имеют больший id)
            const sortedMovies = [...this.movies].sort((a, b) => {
                return b.id - a.id
            })
            return sortedMovies.slice(0, 3)
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
    grid-template-columns: repeat(3, minmax(260px, 1fr));
    gap: 2rem;
    margin: 0 auto; 
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
    flex-wrap: wrap;
}

.movie-meta i {
    margin-right: 4px;
}

.new-badge {
    background: linear-gradient(135deg, #f5c518, #ff8c00);
    padding: 2px 8px;
    border-radius: 20px;
    color: #121212;
    font-weight: bold;
}

.new-badge i {
    color: #121212;
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

/* Стили для раздела "О нас" */
.about-section {
    background: #0f0f13;
    padding: 4rem 0;
    border-top: 1px solid #2c2c30;
}

.about-content h2 {
    text-align: center;
    margin-bottom: 2rem;
    font-size: 2rem;
}

.about-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}

.about-card {
    background: #18181e;
    border-radius: 24px;
    padding: 2rem;
    text-align: center;
    transition: transform 0.25s ease, box-shadow 0.25s;
    border: 1px solid #2c2c30;
}

.about-card:hover {
    transform: translateY(-5px);
    border-color: #f5c518;
    box-shadow: 0 20px 30px -12px rgba(0, 0, 0, 0.5);
}

.about-card i {
    font-size: 3rem;
    color: #f5c518;
    margin-bottom: 1rem;
}

.about-card h3 {
    margin-bottom: 1rem;
    font-size: 1.3rem;
}

.about-card p {
    color: #a1a1aa;
    line-height: 1.5;
}

</style>