import { describe, it, expect } from 'vitest'

describe('Валидация количества билетов', () => {
    const validateTicketCount = (count, remainingSeats) => {
        if (count < 1) return { valid: false, message: 'Количество билетов должно быть не менее 1' }
        if (count > remainingSeats) return { valid: false, message: 'Недостаточно свободных мест' }
        if (count > 10) return { valid: false, message: 'За один раз можно купить не более 10 билетов' }
        return { valid: true, message: '' }
    }

    it('отклоняет 0 билетов', () => {
        const result = validateTicketCount(0, 100)
        expect(result.valid).toBe(false)
        expect(result.message).toContain('не менее 1')
    })

    it('отклоняет отрицательное количество', () => {
        const result = validateTicketCount(-5, 100)
        expect(result.valid).toBe(false)
    })

    it('отклоняет больше доступных мест', () => {
        const result = validateTicketCount(15, 10)
        expect(result.valid).toBe(false)
        expect(result.message).toContain('Недостаточно')
    })

    it('принимает корректное количество', () => {
        const result = validateTicketCount(3, 10)
        expect(result.valid).toBe(true)
    })

    it('отклоняет более 10 билетов', () => {
        const result = validateTicketCount(11, 20)
        expect(result.valid).toBe(false)
        expect(result.message).toContain('не более 10')
    })
})