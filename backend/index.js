const dotenv = require('dotenv');

// Cargar variables de entorno
dotenv.config();

const app = require('./app');
const bootstrap = require('./bootstrap');

const PORT = process.env.PORT || 3000;

bootstrap()
  .then(() => {
    app.listen(PORT, () => {
      console.log(`Servidor corriendo en http://localhost:${PORT}`);
    });
  })
  .catch((error) => {
    console.error('Error al iniciar el servidor:', error.message);
    process.exit(1);
  });

