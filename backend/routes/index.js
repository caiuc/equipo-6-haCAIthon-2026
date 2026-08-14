const express = require('express');
const router = express.Router();

// Importar las rutas creadas
const authRoutes = require('./auth');
const computerRoutes = require('./computer');
const contactRoutes = require('./contact');

// Ruta principal
router.get('/', (req, res) => {
  res.send('¡Bienvenido a la API!');
});

// Rutas de autenticación
router.use('/auth', authRoutes);

// Rutas de computadoras
router.use('/computers', computerRoutes);

// Ruta de contacto
router.use('/contact', contactRoutes);

module.exports = router;