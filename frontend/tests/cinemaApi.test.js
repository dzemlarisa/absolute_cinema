import { describe, it, expect, vi, beforeEach } from 'vitest'
import { cinemaApi } from '../src/api/cinemaApi'

global.fetch = vi.fn()

describe('cinemaApi', () => {
    beforeEach(() => {
        fetch.mockClear()
        global.localStorage = {
            getItem: vi.fn(),
            setItem: vi.fn(),
            removeItem: vi.fn()
        }
    })

    describe('getMovies', () => {
        it('возвращает список фильмов при успешном запросе', async () => {
            const mockMovies = [
                { id: 1, name: 'Фильм 1', genre: 'драма', price: 300 },
                { id: 2, name: 'Фильм 2', genre: 'комедия', price: 250 }
            ]
            fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockMovies
            })

            const result = await cinemaApi.getMovies()
            expect(result).toEqual(mockMovies)
            expect(fetch).toHaveBeenCalledTimes(1)
        })

        it('выбрасывает ошибку при неудачном запросе', async () => {
            fetch.mockResolvedValueOnce({
                ok: false,
                status: 500
            })

            await expect(cinemaApi.getMovies()).rejects.toThrow('Ошибка загрузки фильмов')
        })
    })

    describe('getCinemas', () => {
        it('возвращает список кинотеатров', async () => {
            const mockCinemas = [
                { id: 1, name: 'Кинотеатр 1', address: 'ул. Тестовая, 1' }
            ]
            fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockCinemas
            })

            const result = await cinemaApi.getCinemas()
            expect(result).toEqual(mockCinemas)
        })
    })

    describe('createTicket', () => {
        it('отправляет POST запрос на создание билета', async () => {
            const ticketData = { session_id: 5, ticket_cnt: 2 }
            const mockResponse = { id: 10, total: 700 }
            
            fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockResponse
            })

            const result = await cinemaApi.createTicket(ticketData)
            expect(result).toEqual(mockResponse)
            expect(fetch).toHaveBeenCalledWith(
                expect.stringContaining('/tickets'),
                expect.objectContaining({
                    method: 'POST',
                    body: JSON.stringify(ticketData)
                })
            )
        })
    })

    describe('login', () => {
        it('отправляет запрос на вход и сохраняет токен', async () => {
            const mockResponse = {
                access_token: 'test-token',
                user: { id: 1, name: 'Тест', role: 'client' }
            }
            fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockResponse
            })

            const result = await cinemaApi.login('89991234567', 'password')
            expect(result).toEqual(mockResponse)
            expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', 'test-token')
            expect(localStorage.setItem).toHaveBeenCalledWith('user_data', JSON.stringify(mockResponse.user))
        })

        it('выбрасывает ошибку при неверных данных', async () => {
            fetch.mockResolvedValueOnce({
                ok: false,
                json: async () => ({ detail: 'Неверный телефон или пароль' })
            })

            await expect(cinemaApi.login('wrong', 'wrong')).rejects.toThrow('Неверный телефон или пароль')
        })
    })
})