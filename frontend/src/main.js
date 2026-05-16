import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import axios from 'axios';

import HomePage from './views/HomePage.vue'
import MoviesPage from './views/MoviesPage.vue'
import CinemasPage from './views/CinemasPage.vue'
import TicketPage from './views/TicketPage.vue'

const routes = [
    { path: '/', name: 'home', component: HomePage },
    { path: '/movies', name: 'movies', component: MoviesPage },
    { path: '/cinemas', name: 'cinemas', component: CinemasPage },
    { path: '/ticket', name: 'ticket', component: TicketPage }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')

axios.defaults.baseURL = 'http://localhost:8001';

axios.interceptors.request.use(config => {
    const token = localStorage.getItem('auth_token');
    const tokenType = localStorage.getItem('token_type') || 'bearer';
    
    if (token) {
        config.headers.Authorization = `${tokenType} ${token}`;
    }
    
    return config;
});

axios.interceptors.response.use(
    response => response,
    error => {
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('auth_token');
            localStorage.removeItem('token_type');
            localStorage.removeItem('user_data');
            
            if (window.location.pathname !== '/') {
                window.location.href = '/';
            }
        }
        return Promise.reject(error);
    }
);