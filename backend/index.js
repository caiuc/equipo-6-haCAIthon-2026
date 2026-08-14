const app = require('./app');
const dotenv = require('dotenv');

// Cargar variables de entorno
dotenv.config();

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Servidor corriendo en http://localhost:${PORT}`);
});

