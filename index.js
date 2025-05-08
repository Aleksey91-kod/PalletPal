const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
const dotenv = require('dotenv');

// Загрузка переменных окружения
dotenv.config();

// Создание экземпляра приложения
const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Подключение к базе данных
mongoose.connect(process.env.MONGODB_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true
})
.then(() => console.log('Успешное подключение к MongoDB'))
.catch((err) => console.error('Ошибка подключения к MongoDB:', err));

// Базовый маршрут
app.get('/', (req, res) => {
    res.json({ message: 'Добро пожаловать в API PalletPal' });
});

// Импорт маршрутов
const palletRoutes = require('./routes/pallet.routes');
app.use('/api/pallets', palletRoutes);

// Обработка ошибок
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({
        message: 'Что-то пошло не так!',
        error: process.env.NODE_ENV === 'development' ? err.message : {}
    });
});

// Запуск сервера
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Сервер запущен на порту ${PORT}`);
}); 