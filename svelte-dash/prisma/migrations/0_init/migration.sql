-- CreateTable
CREATE TABLE "Device" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL,
    "calibration" BOOLEAN,
    "location" TEXT,
    "areaServed" TEXT,
    "timestamp" DATETIME NOT NULL
);

-- CreateTable
CREATE TABLE "Camera" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "timestamp" DATETIME NOT NULL,
    "picture" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "WeatherStationVirtual" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "timestamp" DATETIME NOT NULL,
    "temperature" REAL NOT NULL,
    "pressure" REAL NOT NULL,
    "humidity" REAL NOT NULL,
    "wind_speed" REAL NOT NULL,
    "wind_deg" REAL NOT NULL,
    "rain" REAL NOT NULL,
    "deviceId" INTEGER NOT NULL,
    CONSTRAINT "WeatherStationVirtual_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "Device" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "WeatherStation" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "timestamp" DATETIME NOT NULL,
    "Battery_Voltage" REAL NOT NULL,
    "Solar_Panel_Voltage" REAL NOT NULL,
    "Temperature" REAL NOT NULL,
    "Pressure" REAL NOT NULL,
    "Humidity" REAL NOT NULL,
    "GasResistance" REAL NOT NULL,
    "Altitude" REAL NOT NULL,
    "Ts_1" REAL NOT NULL,
    "Ts_2" REAL NOT NULL,
    "Ts_3" REAL NOT NULL,
    "Us_1" REAL NOT NULL,
    "Us_2" REAL NOT NULL,
    "Us_3" REAL NOT NULL,
    "W_vel" REAL NOT NULL,
    "W_dir" REAL NOT NULL,
    "deviceId" INTEGER NOT NULL,
    CONSTRAINT "WeatherStation_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "Device" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "ETRometer" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "timestamp" DATETIME NOT NULL,
    "name" TEXT NOT NULL,
    "charge" REAL NOT NULL,
    "CO2" REAL NOT NULL,
    "TC" REAL NOT NULL,
    "RH" REAL NOT NULL,
    "deviceId" INTEGER NOT NULL,
    CONSTRAINT "ETRometer_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "Device" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "Units" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL,
    "value" TEXT NOT NULL,
    "type" TEXT NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "WeatherStationVirtual_deviceId_key" ON "WeatherStationVirtual"("deviceId");

-- CreateIndex
CREATE UNIQUE INDEX "WeatherStation_deviceId_key" ON "WeatherStation"("deviceId");

-- CreateIndex
CREATE UNIQUE INDEX "Units_name_key" ON "Units"("name");

