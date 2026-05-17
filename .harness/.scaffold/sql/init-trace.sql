CREATE TABLE IF NOT EXISTS trace_nodes (
    id          TEXT PRIMARY KEY,
    type        TEXT NOT NULL CHECK(type IN ('requirement','analysis','decision','task','implementation','fix','optimization','test','bug','review')),
    title       TEXT NOT NULL,
    status      TEXT DEFAULT 'draft',
    phase       TEXT,
    file_path   TEXT,
    commit_hash TEXT,
    metadata    TEXT,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trace_edges (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    from_id     TEXT NOT NULL,
    to_id       TEXT NOT NULL,
    relation    TEXT NOT NULL,
    note        TEXT,
    created_at  TEXT NOT NULL,
    FOREIGN KEY (from_id) REFERENCES trace_nodes(id),
    FOREIGN KEY (to_id) REFERENCES trace_nodes(id),
    UNIQUE(from_id, to_id, relation)
);

CREATE INDEX IF NOT EXISTS idx_nodes_type ON trace_nodes(type);
CREATE INDEX IF NOT EXISTS idx_nodes_status ON trace_nodes(status);
CREATE INDEX IF NOT EXISTS idx_edges_from ON trace_edges(from_id);
CREATE INDEX IF NOT EXISTS idx_edges_to ON trace_edges(to_id);
CREATE INDEX IF NOT EXISTS idx_edges_relation ON trace_edges(relation);

CREATE VIEW IF NOT EXISTS v_node_trace_stats AS
SELECT
    n.id, n.type, n.title, n.status,
    COUNT(DISTINCT e_from.id) AS upstream_count,
    COUNT(DISTINCT e_to.id) AS downstream_count
FROM trace_nodes n
LEFT JOIN trace_edges e_from ON n.id = e_from.to_id
LEFT JOIN trace_edges e_to ON n.id = e_to.from_id
GROUP BY n.id;
