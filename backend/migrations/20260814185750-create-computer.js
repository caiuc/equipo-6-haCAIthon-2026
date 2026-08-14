'use strict';
/** @type {import('sequelize-cli').Migration} */
module.exports = {
  async up(queryInterface, Sequelize) {
    await queryInterface.createTable('Computers', {
      id: {
        allowNull: false,
        autoIncrement: true,
        primaryKey: true,
        type: Sequelize.INTEGER
      },
      name: {
        type: Sequelize.STRING
      },
      owner: {
        type: Sequelize.STRING
      },
      type: {
        type: Sequelize.STRING
      },
      processor: {
        type: Sequelize.STRING
      },
      ramType: {
        type: Sequelize.STRING
      },
      ramCapacity: {
        type: Sequelize.INTEGER
      },
      storageType: {
        type: Sequelize.STRING
      },
      storageCapacity: {
        type: Sequelize.INTEGER
      },
      graphics: {
        type: Sequelize.STRING
      },
      comment: {
        type: Sequelize.STRING
      },
      createdAt: {
        allowNull: false,
        type: Sequelize.DATE
      },
      updatedAt: {
        allowNull: false,
        type: Sequelize.DATE
      }
    });
  },
  async down(queryInterface, Sequelize) {
    await queryInterface.dropTable('Computers');
  }
};