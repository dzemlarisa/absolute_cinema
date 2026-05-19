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
        // Сохраняем токен
        if (data.access_token) {
            localStorage.setItem('auth_token', data.access_token)
        }
        return data
    },

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
        // Сохраняем токен
        if (data.access_token) {
            localStorage.setItem('auth_token', data.access_token)
        }
        return data
    },

    async logout() {
        localStorage.removeItem('auth_token')
        // Можно также вызвать бэкенд для выхода
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
    // Фильмы
    async getMovies(params = {}) {
        const queryParams = new URLSearchParams(params).toString()
        const url = `${API_BASE_URL}/movies${queryParams ? '?' + queryParams : ''}`
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('auth_token') || 'demo'}`
            }
        })
        if (!response.ok) throw new Error('Ошибка загрузки фильмов')
        return response.json()
    },

    async getMovie(id) {
        const response = await fetch(`${API_BASE_URL}/movies/${id}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('auth_token') || 'demo'}`
            }
        })
        if (!response.ok) throw new Error('Ошибка загрузки фильма')
        return response.json()
    },

    async getGenres() {
        const response = await fetch(`${API_BASE_URL}/movies/genres`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('auth_token') || 'demo'}`
            }
        })
        if (!response.ok) throw new Error('Ошибка загрузки жанров')
        return response.json()
    },

    // Кинотеатры
    async getCinemas() {
        const response = await fetch(`${API_BASE_URL}/cinemas`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('auth_token') || 'demo'}`
            }
        })
        if (!response.ok) throw new Error('Ошибка загрузки кинотеатров')
        return response.json()
    },

    async getCinema(id) {
        const response = await fetch(`${API_BASE_URL}/cinemas/${id}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('auth_token') || 'demo'}`
            }
        })
        if (!response.ok) throw new Error('Ошибка загрузки кинотеатра')
        return response.json()
    },

    async getCinemaHalls(cinemaId) {
        const response = await fetch(`${API_BASE_URL}/cinemas/${cinemaId}/halls`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('auth_token') || 'demo'}`
            }
        })
        if (!response.ok) throw new Error('Ошибка загрузки залов')
        return response.json()
    },

    // Сеансы
    async getSessions(params = {}) {
        const queryParams = new URLSearchParams(params).toString()
        const url = `${API_BASE_URL}/sessions${queryParams ? '?' + queryParams : ''}`
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('auth_token') || 'demo'}`
            }
        })
        if (!response.ok) throw new Error('Ошибка загрузки сеансов')
        return response.json()
    },

    async getMovieSessions(movieId) {
        const response = await fetch(`${API_BASE_URL}/movies/${movieId}/sessions`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('auth_token') || 'demo'}`
            }
        })
        if (!response.ok) throw new Error('Ошибка загрузки сеансов фильма')
        return response.json()
    },

    async getCinemaSessions(cinemaId) {
        const response = await fetch(`${API_BASE_URL}/cinemas/${cinemaId}/sessions`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('auth_token') || 'demo'}`
            }
        })
        if (!response.ok) throw new Error('Ошибка загрузки сеансов кинотеатра')
        return response.json()
    },

    // Билеты
    async createTicket(ticketData) {
        const response = await fetch(`${API_BASE_URL}/tickets`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('auth_token') || 'demo'}`
            },
            body: JSON.stringify(ticketData)
        })
        if (!response.ok) throw new Error('Ошибка создания билета')
        return response.json()
    },

    async getUserTickets() {
        const response = await fetch(`${API_BASE_URL}/tickets`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('auth_token') || 'demo'}`
            }
        })
        if (!response.ok) throw new Error('Ошибка загрузки билетов')
        return response.json()
    }
}