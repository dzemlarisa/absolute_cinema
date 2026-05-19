const API_BASE_URL = 'http://localhost:8001'

export const cinemaApi = {
    async register(userData) {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        })
        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Ошибка регистрации')
        }
        const data = await response.json()
        if (data.access_token) {
            localStorage.setItem('auth_token', data.access_token)
            localStorage.setItem('user_data', JSON.stringify(data.user))
        }
        return data
    },

    async logout() {
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user_data')
        try {
            await fetch(`${API_BASE_URL}/auth/logout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                }
            })
        } catch (error) {
            console.error('Ошибка при выходе:', error)
        }
    },

    async getCurrentUser() {
        const auth_token = localStorage.getItem('auth_token')
        if (!auth_token) throw new Error('Не авторизован')
        
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${auth_token}`
            }
        })
        if (!response.ok) throw new Error('Ошибка получения пользователя')
        return response.json()
    },

    // Обновите метод login, чтобы он сохранял роль
    async login(phone, password) {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ phone, password })
        })
        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Ошибка входа')
        }
        const data = await response.json()
        if (data.access_token) {
            localStorage.setItem('auth_token', data.access_token)
            // Сохраняем данные пользователя с ролью
            localStorage.setItem('user_data', JSON.stringify(data.user))
        }
        return data
    },

    getAuthHeaders() {
        const token = localStorage.getItem('auth_token')
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token || 'demo'}`
        }
    },

    // ========== ФИЛЬМЫ ==========
    async getMovies(params = {}) {
        const queryParams = new URLSearchParams(params).toString()
        const url = `${API_BASE_URL}/movies${queryParams ? '?' + queryParams : ''}`
        const response = await fetch(url, {
            headers: this.getAuthHeaders()
        })
        if (!response.ok) throw new Error('Ошибка загрузки фильмов')
        return response.json()
    },

    async getMovie(id) {
        const response = await fetch(`${API_BASE_URL}/movies/${id}`, {
            headers: this.getAuthHeaders()
        })
        if (!response.ok) throw new Error('Ошибка загрузки фильма')
        return response.json()
    },

    async getGenres() {
        const response = await fetch(`${API_BASE_URL}/movies/genres`, {
            headers: this.getAuthHeaders()
        })
        if (!response.ok) throw new Error('Ошибка загрузки жанров')
        return response.json()
    },

    // СОЗДАНИЕ ФИЛЬМА (для админа)
    async createMovie(movieData) {
        const response = await fetch(`${API_BASE_URL}/movies`, {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(movieData)
        })
        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Ошибка создания фильма')
        }
        return response.json()
    },

    // ОБНОВЛЕНИЕ ФИЛЬМА (для админа)
    async updateMovie(id, movieData) {
        const response = await fetch(`${API_BASE_URL}/movies/${id}`, {
            method: 'PUT',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(movieData)
        })
        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Ошибка обновления фильма')
        }
        return response.json()
    },

    // УДАЛЕНИЕ ФИЛЬМА (для админа)
    async deleteMovie(id) {
        const response = await fetch(`${API_BASE_URL}/movies/${id}`, {
            method: 'DELETE',
            headers: this.getAuthHeaders()
        })
        if (!response.ok) throw new Error('Ошибка удаления фильма')
        return response.json()
    },

    // ========== КИНОТЕАТРЫ ==========
    async getCinemas() {
        const response = await fetch(`${API_BASE_URL}/cinemas`, {
            headers: this.getAuthHeaders()
        })
        if (!response.ok) throw new Error('Ошибка загрузки кинотеатров')
        return response.json()
    },

    async getCinema(id) {
        const response = await fetch(`${API_BASE_URL}/cinemas/${id}`, {
            headers: this.getAuthHeaders()
        })
        if (!response.ok) throw new Error('Ошибка загрузки кинотеатра')
        return response.json()
    },

    async getCinemaHalls(cinemaId) {
        const response = await fetch(`${API_BASE_URL}/cinemas/${cinemaId}/halls`, {
            headers: this.getAuthHeaders()
        })
        if (!response.ok) throw new Error('Ошибка загрузки залов')
        return response.json()
    },

    // СОЗДАНИЕ КИНОТЕАТРА (для админа)
    async createCinema(cinemaData) {
        const response = await fetch(`${API_BASE_URL}/cinemas`, {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(cinemaData)
        })
        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Ошибка создания кинотеатра')
        }
        return response.json()
    },

    // ОБНОВЛЕНИЕ КИНОТЕАТРА (для админа)
    async updateCinema(id, cinemaData) {
        const response = await fetch(`${API_BASE_URL}/cinemas/${id}`, {
            method: 'PUT',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(cinemaData)
        })
        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Ошибка обновления кинотеатра')
        }
        return response.json()
    },

    async deleteCinema(id) {
        const response = await fetch(`${API_BASE_URL}/cinemas/${id}`, {
            method: 'DELETE',
            headers: this.getAuthHeaders()
        })
        if (!response.ok) throw new Error('Ошибка удаления кинотеатра')
        return response.json()
    },

    // ========== ЗАЛЫ ==========
    // СОЗДАНИЕ ЗАЛА (для админа)
    async createHall(cinemaId, hallData) {
        const response = await fetch(`${API_BASE_URL}/cinemas/${cinemaId}/halls`, {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(hallData)
        })
        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Ошибка создания зала')
        }
        return response.json()
    },

    async updateHall(id, hallData) {
        const response = await fetch(`${API_BASE_URL}/halls/${id}`, {
            method: 'PUT',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(hallData)
        })
        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Ошибка обновления зала')
        }
        return response.json()
    },

    async deleteHall(id) {
        const response = await fetch(`${API_BASE_URL}/halls/${id}`, {
            method: 'DELETE',
            headers: this.getAuthHeaders()
        })
        if (!response.ok) throw new Error('Ошибка удаления зала')
        return response.json()
    },

    // ========== СЕАНСЫ ==========
    async getSessions(params = {}) {
        const queryParams = new URLSearchParams(params).toString()
        const url = `${API_BASE_URL}/sessions${queryParams ? '?' + queryParams : ''}`
        const response = await fetch(url, {
            headers: this.getAuthHeaders()
        })
        if (!response.ok) throw new Error('Ошибка загрузки сеансов')
        return response.json()
    },

    async getMovieSessions(movieId) {
        const response = await fetch(`${API_BASE_URL}/movies/${movieId}/sessions`, {
            headers: this.getAuthHeaders()
        })
        if (!response.ok) throw new Error('Ошибка загрузки сеансов фильма')
        return response.json()
    },

    async getCinemaSessions(cinemaId) {
        const response = await fetch(`${API_BASE_URL}/cinemas/${cinemaId}/sessions`, {
            headers: this.getAuthHeaders()
        })
        if (!response.ok) throw new Error('Ошибка загрузки сеансов кинотеатра')
        return response.json()
    },

    async createSession(sessionData) {
        const response = await fetch(`${API_BASE_URL}/sessions`, {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(sessionData)
        })
        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Ошибка создания сеанса')
        }
        return response.json()
    },

    async deleteSession(id) {
        const response = await fetch(`${API_BASE_URL}/sessions/${id}`, {
            method: 'DELETE',
            headers: this.getAuthHeaders()
        })
        if (!response.ok) throw new Error('Ошибка удаления сеанса')
        return response.json()
    },

    // ========== БИЛЕТЫ ==========
    async createTicket(ticketData) {
        const response = await fetch(`${API_BASE_URL}/tickets`, {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify(ticketData)
        })
        if (!response.ok) {
            const error = await response.json()
            throw new Error(error.detail || 'Ошибка создания билета')
        }
        return response.json()
    },

    async getUserTickets() {
        const response = await fetch(`${API_BASE_URL}/tickets`, {
            headers: this.getAuthHeaders()
        })
        if (!response.ok) throw new Error('Ошибка загрузки билетов')
        return response.json()
    }
}