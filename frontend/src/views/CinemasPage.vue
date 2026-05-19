<template>
    <div class="cinemas-page">
        <section class="hero">
            <div class="container">
                <h1>Кинотеатры</h1>
                <p>Лучшие залы, удобное расположение</p>
                <button v-if="isAdmin" class="btn-create" @click="openCreateCinemaModal">
                    + Создать кинотеатр
                </button>
            </div>
        </section>

        <section class="cinemas-section">
            <div class="container">
                <div v-if="loading" class="loading">
                    <i class="fas fa-spinner fa-pulse"></i> Загрузка кинотеатров...
                </div>

                <div v-else-if="cinemas.length === 0" class="no-results">
                    <i class="fas fa-building"></i>
                    <p>Кинотеатры не найдены</p>
                </div>

                <div v-else class="cinemas-list">
                    <div v-for="cinema in cinemas" :key="cinema.id" class="cinema-card">
                        <div class="cinema-info">
                            <h3>{{ cinema.name }}</h3>
                            <div class="cinema-address">
                                <i class="fas fa-map-marker-alt"></i> {{ cinema.address }}
                            </div>

                            <div class="halls-info">
                                <div class="halls-header">
                                    <h4>Залы:</h4>
                                    <button v-if="isAdmin" class="btn-add-hall" @click="openCreateHallModal(cinema)">
                                        + Добавить зал
                                    </button>
                                </div>
                                <div v-if="halls[cinema.id] && halls[cinema.id].length" class="halls-list">
                                    <div v-for="hall in halls[cinema.id]" :key="hall.id" class="hall-item">
                                        <span class="hall-badge">
                                            {{ hall.name }} ({{ hall.capacity }} мест)
                                        </span>
                                        <button v-if="isAdmin" class="btn-edit-hall" @click="openEditHallModal(cinema, hall)" title="Редактировать">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                        <button v-if="isAdmin" class="btn-delete-hall" @click="deleteHall(cinema.id, hall.id)" title="Удалить">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </div>
                                </div>
                                <div v-else class="no-halls">
                                    <span>Нет залов</span>
                                </div>
                            </div>

                            <div class="cinema-buttons">
                                <button class="btn-schedule" @click="viewSchedule(cinema.id)">
                                    Расписание и билеты
                                </button>
                                <button v-if="isAdmin" class="btn-delete" @click="deleteCinema(cinema.id)">
                                    Удалить
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <div v-if="showCinemaModal" class="modal-overlay" @click.self="closeCinemaModal">
            <div class="modal-container">
                <div class="modal-header">
                    <h2>{{ isEditingCinema ? 'Редактировать кинотеатр' : 'Создать кинотеатр' }}</h2>
                    <button class="modal-close" @click="closeCinemaModal">&times;</button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="saveCinema">
                        <div class="form-group">
                            <label>Название</label>
                            <input type="text" v-model="cinemaForm.name" required>
                        </div>
                        <div class="form-group">
                            <label>Адрес</label>
                            <input type="text" v-model="cinemaForm.address" required>
                        </div>
                        <div v-if="modalError" class="error-message">{{ modalError }}</div>
                        <div class="modal-actions">
                            <button type="button" class="btn-cancel" @click="closeCinemaModal">Отмена</button>
                            <button type="submit" class="btn-submit" :disabled="modalLoading">
                                {{ modalLoading ? 'Сохранение...' : (isEditingCinema ? 'Сохранить' : 'Создать') }}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <div v-if="showHallModal" class="modal-overlay" @click.self="closeHallModal">
            <div class="modal-container">
                <div class="modal-header">
                    <h2>{{ isEditingHall ? 'Редактировать зал' : 'Создать зал' }}</h2>
                    <button class="modal-close" @click="closeHallModal">&times;</button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="saveHall">
                        <div class="form-group">
                            <label>Название зала</label>
                            <input type="text" v-model="hallForm.name" required>
                        </div>
                        <div class="form-group">
                            <label>Количество мест</label>
                            <input type="number" v-model="hallForm.capacity" required min="1">
                        </div>
                        <div v-if="hallError" class="error-message">{{ hallError }}</div>
                        <div class="modal-actions">
                            <button type="button" class="btn-cancel" @click="closeHallModal">Отмена</button>
                            <button type="submit" class="btn-submit" :disabled="hallLoading">
                                {{ hallLoading ? 'Сохранение...' : (isEditingHall ? 'Сохранить' : 'Создать') }}
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
    name: 'CinemasPage',
    data() {
        return {
            cinemas: [],
            halls: {},
            loading: true,
            isAdmin: false,
            showCinemaModal: false,
            isEditingCinema: false,
            editingCinemaId: null,
            cinemaForm: { name: '', address: '' },
            showHallModal: false,
            isEditingHall: false,
            editingHallId: null,
            currentCinemaForHall: null,
            hallForm: { name: '', capacity: 0 },
            modalLoading: false,
            hallLoading: false,
            modalError: '',
            hallError: ''
        }
    },
    mounted() {
        this.checkAdminStatus();
        this.loadCinemas();
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
        async loadCinemas() {
            this.loading = true;
            try {
                this.cinemas = await cinemaApi.getCinemas();
                await this.loadAllHalls();
            } catch (error) {
                console.error('Ошибка загрузки кинотеатров:', error);
                this.cinemas = [];
            } finally {
                this.loading = false;
            }
        },
        async loadAllHalls() {
            for (const cinema of this.cinemas) {
                try {
                    this.halls[cinema.id] = await cinemaApi.getCinemaHalls(cinema.id);
                } catch (error) {
                    console.error(`Ошибка загрузки залов для ${cinema.name}:`, error);
                    this.halls[cinema.id] = [];
                }
            }
        },
        viewSchedule(cinemaId) {
            this.$router.push({ name: 'ticket', query: { cinemaId } });
        },
        
        openCreateCinemaModal() {
            this.isEditingCinema = false;
            this.editingCinemaId = null;
            this.cinemaForm = { name: '', address: '' };
            this.showCinemaModal = true;
        },
        
        async saveCinema() {
            this.modalLoading = true;
            this.modalError = '';
            try {
                if (this.isEditingCinema) {
                    await cinemaApi.updateCinema(this.editingCinemaId, this.cinemaForm);
                } else {
                    await cinemaApi.createCinema(this.cinemaForm);
                }
                this.closeCinemaModal();
                await this.loadCinemas();
            } catch (error) {
                this.modalError = error.message || 'Ошибка сохранения';
            } finally {
                this.modalLoading = false;
            }
        },
        
        closeCinemaModal() {
            this.showCinemaModal = false;
            this.modalError = '';
        },
        
        async deleteCinema(cinemaId) {
            if (confirm('Вы уверены, что хотите удалить этот кинотеатр?')) {
                try {
                    await cinemaApi.deleteCinema(cinemaId);
                    await this.loadCinemas();
                } catch (error) {
                    alert('Ошибка при удалении кинотеатра');
                }
            }
        },
        
        openCreateHallModal(cinema) {
            this.currentCinemaForHall = cinema;
            this.isEditingHall = false;
            this.editingHallId = null;
            this.hallForm = { name: '', capacity: 0 };
            this.showHallModal = true;
        },
        
        openEditHallModal(cinema, hall) {
            this.currentCinemaForHall = cinema;
            this.isEditingHall = true;
            this.editingHallId = hall.id;
            this.hallForm = { name: hall.name, capacity: hall.capacity };
            this.showHallModal = true;
        },
        
        async saveHall() {
            this.hallLoading = true;
            this.hallError = '';
            try {
                if (this.isEditingHall) {
                    await cinemaApi.updateHall(this.editingHallId, this.hallForm);
                } else {
                    await cinemaApi.createHall(this.currentCinemaForHall.id, this.hallForm);
                }
                this.closeHallModal();
                await this.loadAllHalls();
            } catch (error) {
                this.hallError = error.message || 'Ошибка сохранения зала';
            } finally {
                this.hallLoading = false;
            }
        },
        async deleteHall(cinemaId, hallId) {
            if (confirm('Вы уверены, что хотите удалить этот зал?')) {
                try {
                    await cinemaApi.deleteHall(hallId);
                    await this.loadAllHalls();
                } catch (error) {
                    alert('Ошибка при удалении зала');
                }
            }
        },
        
        closeHallModal() {
            this.showHallModal = false;
            this.hallError = '';
            this.currentCinemaForHall = null;
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
    border: 1px solid #2c2c30;
    transition: transform 0.2s;
}

.cinema-card:hover {
    transform: translateY(-4px);
    border-color: #f5c518;
}

.cinema-info {
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

.halls-info {
    margin: 1rem 0;
}

.halls-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
}

.halls-info h4 {
    font-size: 1rem;
    color: #f5c518;
    margin: 0;
}

.btn-add-hall {
    background: #2c2c34;
    border: none;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.7rem;
    cursor: pointer;
    color: #f5c518;
}

.btn-add-hall:hover {
    background: #f5c518;
    color: #121212;
}

.halls-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.hall-item {
    display: flex;
    align-items: center;
    gap: 0.3rem;
}

.hall-badge {
    background: #25252b;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.75rem;
}

.btn-edit-hall {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 0.7rem;
    opacity: 0.7;
    color: #f5c518;
}

.btn-edit-hall:hover {
    opacity: 1;
}

.no-halls {
    color: #6b6b76;
    font-size: 0.8rem;
    padding: 0.5rem 0;
}

.cinema-buttons {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
}

.btn-schedule {
    background: #f5c518;
    border: none;
    padding: 0.7rem 1.8rem;
    border-radius: 40px;
    font-weight: 700;
    cursor: pointer;
}

.btn-schedule:hover {
    background: #ffda44;
}

.btn-delete {
    background: #dc2626;
    border: none;
    padding: 0.7rem 1.8rem;
    border-radius: 40px;
    font-weight: 700;
    cursor: pointer;
    color: white;
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

.modal-actions {
    display: flex;
    gap: 1rem;
    margin-top: 20px;
}

.btn-cancel {
    flex: 1;
    padding: 10px;
    background: #2c2c34;
    border: 1px solid #3a3a42;
    border-radius: 8px;
    color: white;
    font-weight: 500;
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
    border-radius: 8px;
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
    border-radius: 8px;
    margin-bottom: 15px;
    font-size: 0.9rem;
    text-align: center;
}
.btn-delete-hall {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 0.7rem;
    opacity: 0.7;
    color: #ef4444;

}

.btn-delete-hall:hover {
    opacity: 1;
}

@media (max-width: 768px) {
    .cinema-card {
        flex-direction: column;
    }
    .cinema-buttons {
        flex-direction: column;
    }
    .modal-actions {
        flex-direction: column;
    }
}
</style>