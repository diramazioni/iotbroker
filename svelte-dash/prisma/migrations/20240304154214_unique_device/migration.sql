/*
  Warnings:

  - You are about to drop the column `timestamp` on the `Device` table. All the data in the column will be lost.

*/
-- DropIndex
DROP INDEX "WeatherStation_deviceId_key";

-- DropIndex
DROP INDEX "WeatherStationStd_deviceId_key";

-- DropIndex
DROP INDEX "WeatherStationVirtual_deviceId_key";

-- AlterTable
ALTER TABLE "Device" DROP COLUMN "timestamp";
