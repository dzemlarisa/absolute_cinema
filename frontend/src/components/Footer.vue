<template>
    <footer class="main-footer">
        <div class="container footer-container">
            <div class="footer-col">
                <h4>Absolute cinema</h4>
                <p>Самый удобный сервис покупки билетов в любой кинотеатр города.</p>
            </div>
            <div class="footer-col">
                <h4>Контакты</h4>
                <p>+7 (999) 888-77-66</p>
                <p>cinema@absolute.ru</p>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2025 Absolute cinema. Все права защищены.</p>
        </div>
    </footer>
</template>

<script>
export default {
    name: 'Footer'
}
</script>

<style scoped>
.main-footer {
    background: #07070a;
    border-top: 1px solid #222;
    padding: 2.5rem 0 1rem;
    margin-top: auto;
}

.container {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 24px;
}

.footer-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 2rem;
}

.footer-col h4 {
    margin-bottom: 1rem;
    font-size: 1.1rem;
    color: #f5c518;
}

.footer-col p {
    color: #a3a3b0;
    font-size: 0.85rem;
    margin: 0.5rem 0;
}

.footer-col i {
    margin-right: 8px;
    width: 20px;
}

.footer-bottom {
    text-align: center;
    margin-top: 2.5rem;
    padding-top: 1rem;
    border-top: 1px solid #202024;
    font-size: 0.75rem;
    color: #6b6b76;
}

</style>