const jwt = require('jsonwebtoken');
const createHttpError = require('../error/createHttpError');
require('dotenv').config();

module.exports = (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return next(createHttpError(401, 'No autorizado'));
  }

  const token = authHeader.split(' ')[1];

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded; // Agregar los datos del usuario al objeto `req`
    next();
  } catch (error) {
    next(createHttpError(401, 'Token inválido o expirado'));
  }
};