import { describe, it, expect } from 'vitest'

const validateTicketCount = (count, remainingSeats) => {
    if (count < 1) return { valid: false, message: 'Количество билетов должно быть не менее 1' }
    if (count > remainingSeats) return { valid: false, message: 'Недостаточно свободных мест' }
    if (count > 10) return { valid: false, message: 'За один раз можно купить не более 10 билетов' }
    return { valid: true, message: '' }
}

const validatePhone = (phone) => {
    const phoneRegex = /^[0-9]{11}$/
    if (!phone) return { valid: false, message: 'Телефон обязателен' }
    if (!phoneRegex.test(phone)) return { valid: false, message: 'Введите 11 цифр' }
    return { valid: true, message: '' }
}

const validateName = (name) => {
    if (!name || name.trim().length < 2) {
        return { valid: false, message: 'Имя должно содержать минимум 2 символа' }
    }
    return { valid: true, message: '' }
}

describe('Валидация количества билетов', () => {
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

describe('Валидация телефона', () => {
    it('отклоняет пустой телефон', () => {
        const result = validatePhone('')
        expect(result.valid).toBe(false)
        expect(result.message).toContain('обязателен')
    })

    it('отклоняет телефон с буквами', () => {
        const result = validatePhone('8999abc4567')
        expect(result.valid).toBe(false)
    })

    it('отклоняет телефон с недостаточным количеством цифр', () => {
        const result = validatePhone('899912345')
        expect(result.valid).toBe(false)
    })

    it('принимает корректный телефон из 11 цифр', () => {
        const result = validatePhone('89991234567')
        expect(result.valid).toBe(true)
    })
})

describe('Валидация имени', () => {
    it('отклоняет пустое имя', () => {
        const result = validateName('')
        expect(result.valid).toBe(false)
    })

    it('отклоняет имя из одной буквы', () => {
        const result = validateName('А')
        expect(result.valid).toBe(false)
    })

    it('принимает корректное имя', () => {
        const result = validateName('Иван Петров')
        expect(result.valid).toBe(true)
    })
})