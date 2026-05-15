const API_BASE_URL = 'http://localhost:8001'

export const cinemaApi = {
    // Фильмы
    async getMovies(params = {}) {
        const queryParams = new URLSearchParams(params).toString()
        const url = `${API_BASE_URL}/movies${queryParams ? '?' + queryParams : ''}`
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token') || 'demo'}`
            }
        })
        if (!response.ok) throw new Error('Ошибка загрузки фильмов')
        return response.json()
    },

    async getMovie(id) {
        const response = await fetch(`${API_BASE_URL}/movies/${id}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token') || 'demo'}`
            }
        })
        if (!response.ok) throw new Error('Ошибка загрузки фильма')
        return response.json()
    },

    async getGenres() {
        const response = await fetch(`${API_BASE_URL}/movies/genres`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token') || 'demo'}`
            }
        })
        if (!response.ok) throw new Error('Ошибка загрузки жанров')
        return response.json()
    },

    // Кинотеатры
    async getCinemas() {
        const response = await fetch(`${API_BASE_URL}/cinemas`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token') || 'demo'}`
            }
        })
        if (!response.ok) throw new Error('Ошибка загрузки кинотеатров')
        return response.json()
    },

    async getCinema(id) {
        const response = await fetch(`${API_BASE_URL}/cinemas/${id}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token') || 'demo'}`
            }
        })
        if (!response.ok) throw new Error('Ошибка загрузки кинотеатра')
        return response.json()
    },

    async getCinemaHalls(cinemaId) {
        const response = await fetch(`${API_BASE_URL}/cinemas/${cinemaId}/halls`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token') || 'demo'}`
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
                'Authorization': `Bearer ${localStorage.getItem('token') || 'demo'}`
            }
        })
        if (!response.ok) throw new Error('Ошибка загрузки сеансов')
        return response.json()
    },

    async getMovieSessions(movieId) {
        const response = await fetch(`${API_BASE_URL}/movies/${movieId}/sessions`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token') || 'demo'}`
            }
        })
        if (!response.ok) throw new Error('Ошибка загрузки сеансов фильма')
        return response.json()
    },

    async getCinemaSessions(cinemaId) {
        const response = await fetch(`${API_BASE_URL}/cinemas/${cinemaId}/sessions`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token') || 'demo'}`
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
                'Authorization': `Bearer ${localStorage.getItem('token') || 'demo'}`
            },
            body: JSON.stringify(ticketData)
        })
        if (!response.ok) throw new Error('Ошибка создания билета')
        return response.json()
    },

    async getUserTickets() {
        const response = await fetch(`${API_BASE_URL}/tickets`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token') || 'demo'}`
            }
        })
        if (!response.ok) throw new Error('Ошибка загрузки билетов')
        return response.json()
    }
}