DELETE FROM "Device"
WHERE id IN (
    SELECT d.id
    FROM "Device" AS d
    LEFT JOIN "ETRometer" AS e ON d.id = e."deviceId"
    LEFT JOIN "WeatherStation" AS ws ON d.id = ws."deviceId"
    LEFT JOIN "WeatherStationVirtual" AS wsv ON d.id = wsv."deviceId"
    LEFT JOIN "WeatherStationStd" AS wss ON d.id = wss."deviceId"
    WHERE e.id IS NULL
      AND ws.id IS NULL
      AND wsv.id IS NULL
      AND wss.id IS NULL
);
