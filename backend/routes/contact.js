// Ruta para manejar el formulario de contacto
router.post('/contact', async (req, res, next) => {
    const { name, email, subject, message } = req.body;
  
    try {
      // Validar los datos del formulario
      if (!name || !email || !subject || !message) {
        throw createHttpError(400, 'Todos los campos son obligatorios');
      }
  
      // Simulación de almacenamiento o envío del mensaje
      console.log('Formulario recibido:', { name, email, subject, message });
  
      // Responder al cliente
      res.status(200).json({ message: 'Formulario enviado correctamente' });
    } catch (error) {
      next(error); // Pasar el error al middleware de manejo de errores
    }
  }); 