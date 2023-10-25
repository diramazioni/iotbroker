-- CreateTable
CREATE TABLE "WeatherStationStd" (
    "id" SERIAL NOT NULL,
    "timestamp" TIMESTAMP(3) NOT NULL,
    "Solar_Radiation" DOUBLE PRECISION NOT NULL,
    "Atmospheric_Pressure" DOUBLE PRECISION NOT NULL,
    "Air_Temperature" DOUBLE PRECISION NOT NULL,
    "Relative_Humidity" DOUBLE PRECISION NOT NULL,
    "Wind_Velocity" DOUBLE PRECISION NOT NULL,
    "Wind_Direction" DOUBLE PRECISION NOT NULL,
    "Rainfall" DOUBLE PRECISION NOT NULL,
    "deviceId" INTEGER NOT NULL,

    CONSTRAINT "WeatherStationStd_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "WeatherStationStd_deviceId_key" ON "WeatherStationStd"("deviceId");

-- AddForeignKey
ALTER TABLE "WeatherStationStd" ADD CONSTRAINT "WeatherStationStd_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "Device"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
