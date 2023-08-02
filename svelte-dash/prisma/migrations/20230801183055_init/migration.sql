-- CreateTable
CREATE TABLE "Device" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL,
    "calibration" BOOLEAN,
    "timestamp" BIGINT NOT NULL
);

-- CreateTable
CREATE TABLE "WeatherStation" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "timestamp" TEXT NOT NULL,
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
    "timestamp" TEXT NOT NULL,
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
CREATE UNIQUE INDEX "WeatherStation_deviceId_key" ON "WeatherStation"("deviceId");

-- CreateIndex
CREATE UNIQUE INDEX "Units_name_key" ON "Units"("name");
