import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

import HomePage from './views/HomePage.vue'
import MoviesPage from './views/MoviesPage.vue'
import CinemasPage from './views/CinemasPage.vue'
import TicketPage from './views/TicketPage.vue'
import SessionsPage from './views/SessionsPage.vue'

const routes = [
    { path: '/', name: 'home', component: HomePage },
    { path: '/movies', name: 'movies', component: MoviesPage },
    { path: '/cinemas', name: 'cinemas', component: CinemasPage },
    { path: '/sessions', name: 'sessions', component: SessionsPage },
    { path: '/ticket', name: 'ticket', component: TicketPage }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')