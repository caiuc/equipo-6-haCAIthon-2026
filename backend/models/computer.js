'use strict';
const {
  Model
} = require('sequelize');
module.exports = (sequelize, DataTypes) => {
  class Computer extends Model {
    /**
     * Helper method for defining associations.
     * This method is not a part of Sequelize lifecycle.
     * The `models/index` file will call this method automatically.
     */
    static associate(models) {
      // define association here
    }
  }
  Computer.init({
    name: DataTypes.STRING,
    owner: DataTypes.STRING,
    type: DataTypes.STRING,
    processor: DataTypes.STRING,
    ramType: DataTypes.STRING,
    ramCapacity: DataTypes.INTEGER,
    storageType: DataTypes.STRING,
    storageCapacity: DataTypes.INTEGER,
    graphics: DataTypes.STRING,
    comment: DataTypes.STRING
  }, {
    sequelize,
    modelName: 'Computer',
  });
  return Computer;
};