'use strict';

const { Client } = require('pg');

// Crea la base de datos indicada en el .env si todavía no existe.
async function ensureDatabaseExists() {
  const { DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME } = process.env;

  const client = new Client({
    host: DB_HOST,
    port: DB_PORT,
    user: DB_USER,
    password: DB_PASS,
    database: 'postgres',
  });

  await client.connect();

  const { rowCount } = await client.query(
    'SELECT 1 FROM pg_database WHERE datname = $1',
    [DB_NAME]
  );

  if (rowCount === 0) {
    await client.query(`CREATE DATABASE "${DB_NAME}"`);
    console.log(`Base de datos "${DB_NAME}" creada.`);
  }

  await client.end();
}

// Crea las tablas (si faltan) y el usuario admin del .env (si no existe).
async function ensureSchemaAndAdmin() {
  const { sequelize, User } = require('./models');
  const { ADMIN_NAME, ADMIN_EMAIL, ADMIN_PASSWORD } = process.env;

  await sequelize.sync();

  const [admin, created] = await User.findOrCreate({
    where: { email: ADMIN_EMAIL },
    defaults: { name: ADMIN_NAME, password: ADMIN_PASSWORD },
  });

  if (created) {
    console.log(`Usuario admin creado: ${admin.email}`);
  }
}

async function bootstrap() {
  try {
    await ensureDatabaseExists();
  } catch (error) {
    throw new Error(
      `No se pudo crear/verificar la base de datos. Revisa que Postgres esté corriendo y que DB_USER tenga permiso CREATEDB. Detalle: ${error.message}`
    );
  }

  await ensureSchemaAndAdmin();
}

module.exports = bootstrap;
