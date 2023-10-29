-- SELECT d.*, wss.*
-- FROM "Device" AS d
-- JOIN "WeatherStationStd" AS wss ON d.id = wss."deviceId"
-- WHERE d."name" = 'WeatherStation_s1'
-- ORDER BY d."timestamp" ASC;

SELECT  d.*, wss.timestamp
FROM "WeatherStationStd" AS wss
JOIN "Device" AS d ON d.id = wss."deviceId"
WHERE d."name" = 'WeatherStation_s1'
ORDER BY d."timestamp" ASC;


SELECT d.*
FROM "Device" AS d
LEFT JOIN "WeatherStationStd" AS wss ON d.id = wss."deviceId"
WHERE wss.id IS NULL;