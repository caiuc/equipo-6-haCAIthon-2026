const express = require('express');
const cors = require('cors');
const routes = require('./routes'); // Importar las rutas desde index.js

const app = express();

app.use(cors({
    origin: 'http://localhost:3001', // Reemplaza con la URL de tu frontend
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], // Métodos permitidos
    credentials: true, // Permitir cookies y encabezados de autenticación
  }));

// Middlewares
app.use(express.json()); // Parsear JSON

// Rutas
app.use('/api', routes); // Prefijo para todas las rutas

// Middleware para el manejo de errores
app.use((err, req, res, next) => {
  console.error(`[${req.method} ${req.url}]`, err);
  const status = err.status || 500;
  res.status(status).json({
    error: status === 500 ? 'Internal server error' : err.message,
  });
});

module.exports = app;