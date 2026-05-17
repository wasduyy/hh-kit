-- Trace downstream: find all descendants of a given node
-- Usage: replace :node_id with the target ID (e.g. 'DEC-003')
WITH RECURSIVE downstream AS (
    SELECT to_id, relation, 1 AS depth
    FROM trace_edges
    WHERE from_id = :node_id
    UNION ALL
    SELECT e.to_id, e.relation, d.depth + 1
    FROM trace_edges e
    JOIN downstream d ON e.from_id = d.to_id
    WHERE d.depth < 10
)
SELECT n.*, d.relation, d.depth
FROM downstream d
JOIN trace_nodes n ON n.id = d.to_id
ORDER BY d.depth;
