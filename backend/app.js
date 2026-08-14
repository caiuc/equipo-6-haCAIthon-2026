const express = require('express');
const routes = require('./routes');

const app = express();

// Middlewares
app.use(express.json()); // Parsear JSON

// Rutas
app.use('/api', routes);

module.exports = app;