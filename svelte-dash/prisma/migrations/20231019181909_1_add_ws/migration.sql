-- CreateTable
CREATE TABLE "WeatherStationStd" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "timestamp" DATETIME NOT NULL,
    "Solar_Radiation" REAL NOT NULL,
    "Atmospheric_Pressure" REAL NOT NULL,
    "Air_Temperature" REAL NOT NULL,
    "Relative_Humidity" REAL NOT NULL,
    "Wind_Velocity" REAL NOT NULL,
    "Wind_Direction" REAL NOT NULL,
    "Rainfall" REAL NOT NULL,
    "deviceId" INTEGER NOT NULL,
    CONSTRAINT "WeatherStationStd_deviceId_fkey" FOREIGN KEY ("deviceId") REFERENCES "Device" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateIndex
CREATE UNIQUE INDEX "WeatherStationStd_deviceId_key" ON "WeatherStationStd"("deviceId");
