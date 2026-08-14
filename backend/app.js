const express = require('express');
const routes = require('./routes'); // Importar las rutas desde index.js

const app = express();

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