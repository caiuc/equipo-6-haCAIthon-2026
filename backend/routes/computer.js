const express = require('express');
const { Computer } = require('../models'); // Modelo de computadoras
const createHttpError = require('../error/createHttpError'); // Para manejar errores
const authenticate = require('../middlewares/authenticate'); // Middleware para verificar el token

const router = express.Router();

// Middleware para verificar que el usuario esté autenticado
router.use(authenticate);

// Obtener todas las computadoras
router.get('/', async (req, res, next) => {
  try {
    const computers = await Computer.findAll();
    res.json(computers);
  } catch (error) {
    next(error);
  }
});

// Agregar una nueva computadora
router.post('/', async (req, res, next) => {
  const { name, owner, type, processor, ramType, ramCapacity, storageType, storageCapacity, graphics, comment } = req.body;

  try {
    const newComputer = await Computer.create({
      name,
      owner,
      type,
      processor,
      ramType,
      ramCapacity,
      storageType,
      storageCapacity,
      graphics,
      comment,
    });

    res.status(201).json(newComputer);
  } catch (error) {
    next(error);
  }
});

// Editar una computadora existente
router.patch('/:id', async (req, res, next) => {
  const { id } = req.params;
  const { name, owner, type, processor, ramType, ramCapacity, storageType, storageCapacity, graphics, comment } = req.body;

  try {
    const computer = await Computer.findByPk(id);
    if (!computer) {
      throw createHttpError(404, 'Computadora no encontrada');
    }

    // Actualizar los campos
    await computer.update({
      name,
      owner,
      type,
      processor,
      ramType,
      ramCapacity,
      storageType,
      storageCapacity,
      graphics,
      comment,
    });

    res.json(computer);
  } catch (error) {
    next(error);
  }
});

module.exports = router;