const express = require('express');
const router = express.Router();

// Importar las rutas creadas
const authRoutes = require('./auth');
const computerRoutes = require('./computer');

// Ruta principal
router.get('/', (req, res) => {
  res.send('¡Bienvenido a la API!');
});

// Rutas de autenticación
router.use('/auth', authRoutes);

// Rutas de computadoras
router.use('/computers', computerRoutes);

router.use('/contact');

module.exports = router;