const express = require('express');
const nodemailer = require('nodemailer');
const createHttpError = require('../error/createHttpError');
require('dotenv').config();

const router = express.Router();

const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: Number(process.env.SMTP_PORT),
  secure: Number(process.env.SMTP_PORT) === 465,
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS,
  },
});

// Ruta para manejar el formulario de contacto
router.post('/', async (req, res, next) => {
  const { name, email, subject, message } = req.body;

  try {
    if (!name || !email || !subject || !message) {
      throw createHttpError(400, 'Todos los campos son obligatorios');
    }

    await transporter.sendMail({
      from: `"${process.env.ADMIN_NAME}" <${process.env.SMTP_USER}>`,
      to: email,
      subject,
      text: `Hola ${name},\n\nHemos recibido tu mensaje:\n\n${message}`,
    });

    res.status(200).json({ message: 'Correo enviado correctamente' });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
