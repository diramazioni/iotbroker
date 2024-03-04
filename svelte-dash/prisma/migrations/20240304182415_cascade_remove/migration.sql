-- DropForeignKey
ALTER TABLE "ETRometer" DROP CONSTRAINT "ETRometer_deviceId_fkey";

-- DropForeignKey
ALTER TABLE "WeatherStation" DROP CONSTRAINT "WeatherStation_deviceId_fkey";

-- DropForeignKey
ALTER TABLE "WeatherStationStd" DROP CONSTRAINT "WeatherStationStd_deviceId_fkey";

-- DropForeignKey
ALTER TABLE "WeatherStationVirtual" DROP CONSTRAINT "WeatherStationVirtual_deviceId_fkey";

-- AddForeignKey
ALTER TABLE "WeatherStationVirtual" ADD CONSTRAINT "WeatherStationVirtual_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "Device"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "WeatherStation" ADD CONSTRAINT "WeatherStation_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "Device"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "WeatherStationStd" ADD CONSTRAINT "WeatherStationStd_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "Device"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ETRometer" ADD CONSTRAINT "ETRometer_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "Device"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
