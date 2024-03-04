UPDATE "WeatherStation"
SET "deviceId" = new_primary_id
FROM (
    SELECT MIN(id) AS new_primary_id, name
    FROM "Device"
    GROUP BY name
) AS new_primary
WHERE "WeatherStation"."deviceId" IN (SELECT id FROM "Device" WHERE name = new_primary.name);

UPDATE "WeatherStationStd"
SET "deviceId" = new_primary_id
FROM (
    SELECT MIN(id) AS new_primary_id, name
    FROM "Device"
    GROUP BY name
) AS new_primary
WHERE "WeatherStationStd"."deviceId" IN (SELECT id FROM "Device" WHERE name = new_primary.name);

UPDATE "WeatherStationVirtual"
SET "deviceId" = new_primary_id
FROM (
    SELECT MIN(id) AS new_primary_id, name
    FROM "Device"
    GROUP BY name
) AS new_primary
WHERE "WeatherStationVirtual"."deviceId" IN (SELECT id FROM "Device" WHERE name = new_primary.name);

UPDATE "ETRometer"
SET "deviceId" = new_primary_id
FROM (
    SELECT MIN(id) AS new_primary_id, name
    FROM "Device"
    GROUP BY name
) AS new_primary
WHERE "ETRometer"."deviceId" IN (SELECT id FROM "Device" WHERE name = new_primary.name);

DELETE FROM "Device"
WHERE id NOT IN (SELECT MIN(id) FROM "Device" GROUP BY name);
