SELECT setval(pg_get_serial_sequence('"Device"', 'id'), coalesce(max(id)+1, 1), false) FROM "Device";
SELECT setval(pg_get_serial_sequence('"ETRometer"', 'id'), coalesce(max(id)+1, 1), false) FROM "ETRometer";
SELECT setval(pg_get_serial_sequence('"WeatherStation"', 'id'), coalesce(max(id)+1, 1), false) FROM "WeatherStation";
SELECT setval(pg_get_serial_sequence('"WeatherStationVirtual"', 'id'), coalesce(max(id)+1, 1), false) FROM "WeatherStationVirtual";
SELECT setval(pg_get_serial_sequence('"Units"', 'id'), coalesce(max(id)+1, 1), false) FROM "Units";
SELECT setval(pg_get_serial_sequence('"WeatherStationStd"', 'id'), coalesce(max(id)+1, 1), false) FROM "WeatherStationStd";