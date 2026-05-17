-- Trace completeness check: find broken chains (supports indirect paths via recursive CTE)

-- Requirements without any downstream decision (direct or indirect)
SELECT 'REQ_NO_DEC' AS issue, n.id, n.title
FROM trace_nodes n
WHERE n.type = 'requirement' AND n.status != 'verified'
AND NOT EXISTS (
    WITH RECURSIVE downstream(node_id) AS (
        SELECT to_id FROM trace_edges WHERE from_id = n.id
        UNION ALL
        SELECT e.to_id FROM trace_edges e JOIN downstream d ON e.from_id = d.node_id
    )
    SELECT 1 FROM downstream d JOIN trace_nodes t ON t.id = d.node_id AND t.type = 'decision'
)

UNION ALL

-- Decisions without any downstream implementation (direct or indirect)
SELECT 'DEC_NO_IMP' AS issue, n.id, n.title
FROM trace_nodes n
WHERE n.type = 'decision' AND n.status = 'accepted'
AND NOT EXISTS (
    WITH RECURSIVE downstream(node_id) AS (
        SELECT to_id FROM trace_edges WHERE from_id = n.id
        UNION ALL
        SELECT e.to_id FROM trace_edges e JOIN downstream d ON e.from_id = d.node_id
    )
    SELECT 1 FROM downstream d JOIN trace_nodes t ON t.id = d.node_id AND t.type IN ('implementation', 'fix', 'optimization')
)

UNION ALL

-- Implementations without any downstream test (direct or indirect)
SELECT 'IMP_NO_TST' AS issue, n.id, n.title
FROM trace_nodes n
WHERE n.type = 'implementation' AND n.status = 'completed'
AND NOT EXISTS (
    WITH RECURSIVE downstream(node_id) AS (
        SELECT to_id FROM trace_edges WHERE from_id = n.id
        UNION ALL
        SELECT e.to_id FROM trace_edges e JOIN downstream d ON e.from_id = d.node_id
    )
    SELECT 1 FROM downstream d JOIN trace_nodes t ON t.id = d.node_id AND t.type = 'test'
)

UNION ALL

-- Bugs without any downstream fix (direct or indirect)
SELECT 'BUG_NO_FIX' AS issue, n.id, n.title
FROM trace_nodes n
WHERE n.type = 'bug' AND n.status != 'resolved'
AND NOT EXISTS (
    WITH RECURSIVE downstream(node_id) AS (
        SELECT to_id FROM trace_edges WHERE from_id = n.id
        UNION ALL
        SELECT e.to_id FROM trace_edges e JOIN downstream d ON e.from_id = d.node_id
    )
    SELECT 1 FROM downstream d JOIN trace_nodes t ON t.id = d.node_id AND t.type = 'fix'
);
