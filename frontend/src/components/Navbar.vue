<template>
    <header class="navbar">
        <div class="container">
            <div class="logo">
                <router-link to="/">Absolute Cinema</router-link>
            </div>
            <nav class="nav-links">
                <router-link to="/" class="nav-link">Главная</router-link>
                <router-link to="/movies" class="nav-link">Фильмы</router-link>
                <router-link to="/cinemas" class="nav-link">Кинотеатры</router-link>
                <router-link to="/ticket" class="nav-link">Купить билет</router-link>
            </nav>
            <div class="auth-buttons">
                <button class="btn-auth" @click="showAuthModal = true">Вход</button>
            </div>
        </div>
    </header>
</template>

<script>
export default {
    name: 'Navbar',
    data() {
        return {
            showAuthModal: false
        }
    }
}
</script>

<style scoped>

.container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
    margin: 0 auto;
    padding: 0 24px;
}

.navbar {
    background: rgba(18, 18, 24, 0.96);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid #2a2a2e;
    position: sticky;
    top: 0;
    z-index: 100;
    padding: 1rem 0;
    width: 100%;
}



.logo a {
    font-size: 1.8rem;
    font-weight: 700;
    color: #f5c518;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 10px;
}

.nav-links {
    display: flex;
    gap: 2rem;
}

.nav-link {
    color: #e2e2e8;
    text-decoration: none;
    font-weight: 500;
    transition: 0.2s;
    padding: 0.5rem 0;
    border-bottom: 2px solid transparent;
}

.nav-link:hover, .nav-link.router-link-active {
    color: #f5c518;
    border-bottom-color: #f5c518;
}

.btn-auth {
    background: #2c2c34;
    border: none;
    padding: 0.6rem 1.4rem;
    border-radius: 40px;
    font-weight: 600;
    color: white;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

.btn-auth:hover {
    background: #f5c518;
    color: #121212;
}
</style>