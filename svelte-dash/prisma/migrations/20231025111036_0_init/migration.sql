-- CreateTable
CREATE TABLE "Device" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "calibration" BOOLEAN,
    "location" TEXT,
    "areaServed" TEXT,
    "timestamp" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Device_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Camera" (
    "id" SERIAL NOT NULL,
    "timestamp" TIMESTAMP(3) NOT NULL,
    "picture" TEXT NOT NULL,

    CONSTRAINT "Camera_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "WeatherStationVirtual" (
    "id" SERIAL NOT NULL,
    "timestamp" TIMESTAMP(3) NOT NULL,
    "temperature" DOUBLE PRECISION NOT NULL,
    "pressure" DOUBLE PRECISION NOT NULL,
    "humidity" DOUBLE PRECISION NOT NULL,
    "wind_speed" DOUBLE PRECISION NOT NULL,
    "wind_deg" DOUBLE PRECISION NOT NULL,
    "rain" DOUBLE PRECISION NOT NULL,
    "deviceId" INTEGER NOT NULL,

    CONSTRAINT "WeatherStationVirtual_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "WeatherStation" (
    "id" SERIAL NOT NULL,
    "timestamp" TIMESTAMP(3) NOT NULL,
    "Battery_Voltage" DOUBLE PRECISION NOT NULL,
    "Solar_Panel_Voltage" DOUBLE PRECISION NOT NULL,
    "Temperature" DOUBLE PRECISION NOT NULL,
    "Pressure" DOUBLE PRECISION NOT NULL,
    "Humidity" DOUBLE PRECISION NOT NULL,
    "GasResistance" DOUBLE PRECISION NOT NULL,
    "Altitude" DOUBLE PRECISION NOT NULL,
    "Ts_1" DOUBLE PRECISION NOT NULL,
    "Ts_2" DOUBLE PRECISION NOT NULL,
    "Ts_3" DOUBLE PRECISION NOT NULL,
    "Us_1" DOUBLE PRECISION NOT NULL,
    "Us_2" DOUBLE PRECISION NOT NULL,
    "Us_3" DOUBLE PRECISION NOT NULL,
    "W_vel" DOUBLE PRECISION NOT NULL,
    "W_dir" DOUBLE PRECISION NOT NULL,
    "deviceId" INTEGER NOT NULL,

    CONSTRAINT "WeatherStation_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ETRometer" (
    "id" SERIAL NOT NULL,
    "timestamp" TIMESTAMP(3) NOT NULL,
    "name" TEXT NOT NULL,
    "charge" DOUBLE PRECISION NOT NULL,
    "CO2" DOUBLE PRECISION NOT NULL,
    "TC" DOUBLE PRECISION NOT NULL,
    "RH" DOUBLE PRECISION NOT NULL,
    "deviceId" INTEGER NOT NULL,

    CONSTRAINT "ETRometer_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Units" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "value" TEXT NOT NULL,
    "type" TEXT NOT NULL,

    CONSTRAINT "Units_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "WeatherStationVirtual_deviceId_key" ON "WeatherStationVirtual"("deviceId");

-- CreateIndex
CREATE UNIQUE INDEX "WeatherStation_deviceId_key" ON "WeatherStation"("deviceId");

-- CreateIndex
CREATE UNIQUE INDEX "Units_name_key" ON "Units"("name");

-- AddForeignKey
ALTER TABLE "WeatherStationVirtual" ADD CONSTRAINT "WeatherStationVirtual_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "Device"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "WeatherStation" ADD CONSTRAINT "WeatherStation_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "Device"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ETRometer" ADD CONSTRAINT "ETRometer_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "Device"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
