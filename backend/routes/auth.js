const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { User } = require('../models'); // Asegúrate de que el modelo User esté configurado
const createHttpError = require('../error/createHttpError'); // Importar createHttpError
require('dotenv').config();

const router = express.Router();

// Ruta de inicio de sesión
router.post('/login', async (req, res, next) => {
  const { email, password } = req.body;

  try {
    const user = await User.findOne({ where: { email } });
    if (!user) {
      throw createHttpError(404, 'Usuario no encontrado');
    }

    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
      throw createHttpError(401, 'Contraseña incorrecta');
    }

    // Generar un token JWT
    const token = jwt.sign({ id: user.id, email: user.email }, process.env.JWT_SECRET, { expiresIn: '1h' });

    res.json({ message: 'Inicio de sesión exitoso', token });
  } catch (error) {
    next(error); // Pasar el error al middleware de manejo de errores
  }
});

// Ruta para recuperar contraseña
router.post('/forgot-password', async (req, res, next) => {
  const { email } = req.body;

  try {
    const user = await User.findOne({ where: { email } });
    if (!user) {
      throw createHttpError(404, 'Usuario no encontrado');
    }

    // Aquí puedes generar un token o un código de recuperación
    const resetToken = jwt.sign({ id: user.id, email: user.email }, process.env.JWT_SECRET, { expiresIn: '15m' });

    // Simulación de envío de correo (puedes usar nodemailer para enviar correos reales)
    console.log(`Token de recuperación para ${email}: ${resetToken}`);

    res.json({ message: 'Se ha enviado un correo con instrucciones para recuperar la contraseña' });
  } catch (error) {
    next(error); // Pasar el error al middleware de manejo de errores
  }
});

module.exports = router;