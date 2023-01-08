SELECT reports.reported_at_ms, app_eui.name, dev_eui.name, reports.dc_balance, reports.fcnt, reports.port, device_names.name, reports.battery_voltage, points.lat, points.lng, points.alt, points.accuracy, points.fix, points.satellites, COUNT(hotspot_connections.id)
FROM ((((((reports
INNER JOIN app_eui ON app_eui.id = reports.app_eui_id)
INNER JOIN dev_eui ON dev_eui.id = reports.dev_eui_id)
INNER JOIN dev_addr ON dev_addr.id = reports.dev_addr_id)
INNER JOIN device_names ON device_names.id = reports.name_id)
INNER JOIN points ON points.report_id = reports.id)
INNER JOIN hotspot_connections ON hotspot_connections.report_id = reports.id)
GROUP BY reports.id;
