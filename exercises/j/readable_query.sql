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
),
creators_with_a_series AS (
    -- The original query qualifies every unit of a creator with any A series.
    SELECT DISTINCT creator_id
    FROM series
    WHERE code = 'A'
)
SELECT
    c.name AS creator_name,
    s.code || '/' || u.ref AS reference,
    u.year_from || '-' || u.year_to AS date_range,
    req.request_count,
    COALESCE(c.county, '?') AS county
FROM creator c
JOIN series s ON s.creator_id = c.id
JOIN unit u ON u.series_id = s.id
JOIN open_requests req ON req.unit_id = u.id
CROSS JOIN avg_requests ar
WHERE u.digitised = 0
  AND u.restricted <> 1
  AND (u.year_to < 1960 OR c.id IN (SELECT creator_id FROM creators_with_a_series))
  AND req.request_count > (ar.global_avg - 1)
ORDER BY req.request_count DESC, date_range;
