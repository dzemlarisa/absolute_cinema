<template>
    <div class="cinemas-page">
        <section class="hero">
            <div class="container">
                <h1>Кинотеатры</h1>
                <p>Лучшие залы, удобное расположение</p>
            </div>
        </section>

        <section class="cinemas-section">
            <div class="container">
                <div v-if="loading" class="loading">
                    <i class="fas fa-spinner fa-pulse"></i> Загрузка кинотеатров...
                </div>

                <div v-else-if="cinemas.length === 0" class="no-results">
                    <p>Кинотеатры не найдены</p>
                </div>

                <div v-else class="cinemas-list">
                    <div v-for="cinema in cinemas" :key="cinema.id" class="cinema-card">
                        <div class="cinema-info">
                            <h3>{{ cinema.name }}</h3>
                            <div class="cinema-address">
                                <i class="fas fa-map-marker-alt"></i> {{ cinema.address }}
                            </div>

                            <div class="halls-info" v-if="halls[cinema.id]">
                                <h4>Залы:</h4>
                                <div class="halls-list">
                                    <span v-for="hall in halls[cinema.id]" :key="hall.id" class="hall-badge">
                                        {{ hall.name }} ({{ hall.capacity }} мест)
                                    </span>
                                </div>
                            </div>
                            <button class="btn-schedule" @click="viewSchedule(cinema.id)">
                                Расписание и билеты
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
    name: 'CinemasPage',
    data() {
        return {
            cinemas: [],
            halls: {},
            loading: true
        }
    },
    async mounted() {
        await this.loadCinemas()
        await this.loadAllHalls()
        this.loading = false
    },
    methods: {
        async loadCinemas() {
            try {
                this.cinemas = await cinemaApi.getCinemas()
            } catch (error) {
                console.error('Ошибка загрузки кинотеатров:', error)
                this.cinemas = []
            }
        },
        async loadAllHalls() {
            for (const cinema of this.cinemas) {
                try {
                    this.halls[cinema.id] = await cinemaApi.getCinemaHalls(cinema.id)
                } catch (error) {
                    this.halls[cinema.id] = []
                }
            }
        },
        getCinemaFeatures(cinema) {
            const features = [
                { icon: 'fas fa-film', text: 'Современные залы' }
            ]
            if (cinema.has_imax) features.push({ icon: 'fas fa-star', text: 'IMAX' })
            if (cinema.has_vip) features.push({ icon: 'fas fa-crown', text: 'VIP залы' })
            return features
        },
        viewSchedule(cinemaId) {
            this.$router.push({ name: 'ticket', query: { cinemaId } })
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

.cinemas-section {
    padding: 3rem 0;
}

.container {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 24px;
}

.cinemas-list {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.cinema-card {
    background: #18181e;
    border-radius: 24px;
    overflow: hidden;
    display: flex;
    flex-wrap: wrap;
    border: 1px solid #2c2c30;
    transition: transform 0.2s;
}

.cinema-card:hover {
    transform: translateY(-4px);
    border-color: #f5c518;
}

.cinema-image {
    flex: 1;
    min-width: 250px;
    max-height: 260px;
    overflow: hidden;
}

.cinema-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.cinema-info {
    flex: 2;
    padding: 1.5rem;
}

.cinema-info h3 {
    font-size: 1.6rem;
    color: #f5c518;
    margin-bottom: 0.5rem;
}

.cinema-address {
    color: #b9b9c3;
    margin-bottom: 1rem;
}

.cinema-features {
    display: flex;
    flex-wrap: wrap;
    gap: 0.8rem;
    margin-bottom: 1rem;
}

.cinema-features span {
    background: #2a2a30;
    padding: 0.3rem 0.9rem;
    border-radius: 30px;
    font-size: 0.8rem;
}

.halls-info {
    margin: 1rem 0;
}

.halls-info h4 {
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
    color: #f5c518;
}

.halls-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.hall-badge {
    background: #25252b;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.75rem;
}

.btn-schedule {
    background: #f5c518;
    border: none;
    padding: 0.7rem 1.8rem;
    border-radius: 40px;
    font-weight: 700;
    cursor: pointer;
    margin-top: 0.5rem;
}

.btn-schedule:hover {
    background: #ffda44;
}

.loading, .no-results {
    text-align: center;
    padding: 3rem;
}

@media (max-width: 768px) {
    .cinema-card {
        flex-direction: column;
    }
    .cinema-image {
        max-height: 200px;
    }
}
</style>