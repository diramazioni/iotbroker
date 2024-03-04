-- UPDATE "WeatherStation"
-- SET "deviceId" = new_primary_id
-- FROM (
--     SELECT MIN(id) AS new_primary_id, name
--     FROM "Device"
--     GROUP BY name
-- ) AS new_primary
-- WHERE "WeatherStation"."deviceId" IN (SELECT id FROM "Device" WHERE name = new_primary.name);
CREATE TEMP TABLE temp_primary_mapping AS
SELECT MIN(id) AS new_primary_id, name
FROM "Device"
GROUP BY name;

UPDATE "WeatherStationStd"
SET "deviceId" =  temp.new_primary_id
FROM temp_primary_mapping temp
WHERE "WeatherStationStd"."deviceId" IN (SELECT id FROM "Device" WHERE name = temp.name);

UPDATE "WeatherStationVirtual"
SET "deviceId" =  temp.new_primary_id
FROM temp_primary_mapping temp
WHERE "WeatherStationVirtual"."deviceId" IN (SELECT id FROM "Device" WHERE name = temp.name);

UPDATE "ETRometer"
SET "deviceId" =  temp.new_primary_id
FROM temp_primary_mapping temp
WHERE "ETRometer"."deviceId" IN (SELECT id FROM "Device" WHERE name = temp.name);

DELETE FROM "Device"
WHERE id NOT IN (SELECT MIN(id) FROM "Device" GROUP BY name);

