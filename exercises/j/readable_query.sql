-- Candidates for digitization (based on request volume and age)
WITH open_requests AS (
    -- Count open requests per unit since start of 2024
    SELECT 
        unit_id, 
        COUNT(*) AS request_count 
    FROM request 
    WHERE status NOT IN ('rejected', 'cancelled', 'done') 
      AND requested >= '2024-01-01' 
    GROUP BY unit_id
),
avg_requests AS (
    -- Calculate the average number of open requests per unit
    SELECT 
        COUNT(*) * 1.0 / COUNT(DISTINCT unit_id) AS global_avg
    FROM request 
    WHERE status = 'open'
)
SELECT 
    c.name AS creator_name, 
    s.code || '/' || u.ref AS reference, 
    u.year_from || '-' || u.year_to AS date_range, 
    or.request_count, 
    COALESCE(c.county, '?') AS county
FROM creator c
JOIN series s ON s.creator_id = c.id
JOIN unit u ON u.series_id = s.id
JOIN open_requests or ON or.unit_id = u.id
CROSS JOIN avg_requests ar
WHERE u.digitised = 0 
  AND u.restricted <> 1
  AND (u.year_to < 1960 OR s.code = 'A')
  AND or.request_count > (ar.global_avg - 1)
ORDER BY or.request_count DESC, date_range;
