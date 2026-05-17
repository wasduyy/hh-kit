-- Trace statistics by type and status
SELECT type, status, COUNT(*) AS count
FROM trace_nodes
GROUP BY type, status
ORDER BY type, status;
