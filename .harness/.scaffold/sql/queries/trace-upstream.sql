-- Trace upstream: find all ancestors of a given node
-- Usage: replace :node_id with the target ID (e.g. 'BUG-003')
WITH RECURSIVE upstream AS (
    SELECT from_id, relation, 1 AS depth
    FROM trace_edges
    WHERE to_id = :node_id
    UNION ALL
    SELECT e.from_id, e.relation, u.depth + 1
    FROM trace_edges e
    JOIN upstream u ON e.to_id = u.from_id
    WHERE u.depth < 10
)
SELECT n.*, u.relation, u.depth
FROM upstream u
JOIN trace_nodes n ON n.id = u.from_id
ORDER BY u.depth;
