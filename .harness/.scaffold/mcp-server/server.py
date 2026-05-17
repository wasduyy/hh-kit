"""hh-kit MCP Server - Scaffold Tool Provider."""

import glob
import json
import os
import re
import sqlite3
from datetime import datetime

from mcp.server import Server

_SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(_SERVER_DIR)))
CONTROL_DIR = os.path.join(_PROJECT_DIR, ".control")
KNOWLEDGE_DIR = os.path.join(_PROJECT_DIR, "knowledge")
HARNESS_DIR = os.path.join(_PROJECT_DIR, ".harness")
DB_PATH = os.path.join(CONTROL_DIR, "trace.db")


def _read_project_name():
    harness_yml = os.path.join(CONTROL_DIR, "harness.yml")
    if os.path.exists(harness_yml):
        try:
            with open(harness_yml, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("name:"):
                        name = line.split(":", 1)[1].strip().strip('"').strip("'")
                        if name:
                            return name
        except Exception:
            pass
    return None


_project_name = _read_project_name()
_server_name = f"hh-kit--{_project_name}" if _project_name else "hh-kit"
server = Server(_server_name)

TYPE_MAP = {
    "requirement": "REQ", "analysis": "ANA", "decision": "DEC",
    "task": "TSK", "implementation": "IMP", "fix": "FIX",
    "optimization": "OPT", "test": "TST", "bug": "BUG", "review": "REV"
}

TYPE_DIR_MAP = {
    "requirement": "requirements", "analysis": "analysis", "decision": "decisions",
    "task": "tasks", "implementation": "implementations", "fix": "fixes",
    "optimization": "optimizations", "test": "tests", "bug": "bugs", "review": "reviews"
}


def get_db():
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ok(**kwargs):
    return json.dumps({"success": True, **kwargs}, ensure_ascii=False)


def fail(error, **kwargs):
    return json.dumps({"success": False, "error": error, **kwargs}, ensure_ascii=False)


@server.list_tools()
async def list_tools():
    from mcp import types
    return [
        types.Tool(name="trace_create_node", description="Create a traceability node in SQLite",
                   inputSchema={"type": "object", "required": ["id", "type", "title"],
                                "properties": {
                                    "id": {"type": "string", "description": "Trace ID e.g. REQ-001"},
                                    "type": {"type": "string", "enum": list(TYPE_MAP.keys())},
                                    "title": {"type": "string"},
                                    "traces_from": {"type": "array", "items": {"type": "string"}, "default": []},
                                    "status": {"type": "string", "default": "draft"},
                                    "phase": {"type": "string"},
                                    "commit_hash": {"type": "string", "description": "Git commit SHA if applicable"},
                                    "files_changed": {"type": "array", "items": {"type": "string"}, "description": "List of files modified/created"},
                                    "summary": {"type": "string", "description": "Brief description of what was done"}}}),
        types.Tool(name="trace_create_edge", description="Create a trace edge between two nodes",
                   inputSchema={"type": "object", "required": ["from_id", "to_id"],
                                "properties": {
                                    "from_id": {"type": "string"},
                                    "to_id": {"type": "string"},
                                    "relation": {"type": "string", "default": "traces_to"},
                                    "note": {"type": "string", "default": ""}}}),
        types.Tool(name="trace_next_id", description="Get the next available trace ID for a type (max+1, DB is source of truth)",
                   inputSchema={"type": "object", "required": ["type"],
                                "properties": {"type": {"type": "string", "enum": list(TYPE_MAP.keys())}}}),
        types.Tool(name="trace_query", description="Query trace graph upstream or downstream",
                   inputSchema={"type": "object", "required": ["direction", "node_id"],
                                "properties": {
                                    "direction": {"type": "string", "enum": ["upstream", "downstream"]},
                                    "node_id": {"type": "string"}}}),
        types.Tool(name="trace_validate", description="Validate trace chain completeness",
                   inputSchema={"type": "object", "properties": {}}),
        types.Tool(name="trace_stats", description="Get trace node statistics by type and status",
                   inputSchema={"type": "object", "properties": {}}),
        types.Tool(name="trace_report", description="Get full traceability report for a node: node info + upstream chain + downstream chain + files changed + commit. Prefer this over trace_query for single-node inspection.",
                   inputSchema={"type": "object", "required": ["node_id"],
                                "properties": {"node_id": {"type": "string"}}}),
        types.Tool(name="trace_timeline", description="Given a requirement/decision/task ID, recursively find all downstream IMP/FIX/OPT nodes and output as implementation timeline. Prefer this over trace_query for viewing implementation progress.",
                   inputSchema={"type": "object", "required": ["root_id"],
                                "properties": {"root_id": {"type": "string", "description": "Root node ID (e.g. REQ-001, TSK-001)"}}}),
        types.Tool(name="trace_update_node", description="Update a trace node's status, title, or other fields. Use to transition status: draft -> in_progress -> done/accepted.",
                   inputSchema={"type": "object", "required": ["node_id"],
                                "properties": {
                                    "node_id": {"type": "string"},
                                    "status": {"type": "string", "description": "New status: draft, in_progress, done, accepted, completed"},
                                    "title": {"type": "string", "description": "New title (optional)"},
                                    "phase": {"type": "string", "description": "New phase (optional)"},
                                    "commit_hash": {"type": "string", "description": "Git commit SHA (optional)"},
                                    "files_changed": {"type": "array", "items": {"type": "string"}, "description": "Update files_changed in metadata (optional)"},
                                    "summary": {"type": "string", "description": "Update the summary in metadata (optional)"}}}),
        types.Tool(name="gate_check", description="Run gate checks for current or specified phase. Checks trace completeness, requirements coverage, and phase-specific conditions.",
                   inputSchema={"type": "object",
                                "properties": {
                                    "phase": {"type": "string", "description": "Phase to check (defaults to current phase from state.json)"}}}),
        types.Tool(name="sync_all", description="Full sync: update knowledge .md status, state.json milestones, harness.summary.md from DB",
                   inputSchema={"type": "object",
                                "properties": {
                                    "active_context": {"type": "string", "description": "New content for activeContext.md"},
                                    "progress_entry": {"type": "string", "description": "New entry to append to progress.md"}}}),
        types.Tool(name="state_read", description="Read current project phase state",
                   inputSchema={"type": "object", "properties": {}}),
        types.Tool(name="state_advance", description="Advance to the next project phase. Runs gate checks on current phase before advancing.",
                   inputSchema={"type": "object", "required": ["phase_name"],
                                "properties": {
                                    "phase_name": {"type": "string"},
                                    "validation_log": {"type": "string", "default": ""},
                                    "skip_gate": {"type": "boolean", "default": false, "description": "Skip gate checks (use with caution)"}}}),
        types.Tool(name="config_read", description="Read project configuration (harness.yml)",
                   inputSchema={"type": "object", "properties": {}}),
        types.Tool(name="memory_read", description="Read session memory files",
                   inputSchema={"type": "object", "properties": {}}),
        types.Tool(name="memory_update", description="Update a session memory file",
                   inputSchema={"type": "object", "required": ["file_name", "content"],
                                "properties": {
                                    "file_name": {"type": "string", "enum": ["activeContext", "progress"]},
                                    "content": {"type": "string"}}}),
    ]


@server.call_tool()
async def call_tool(name, arguments):
    result = _dispatch(name, arguments or {})
    from mcp import types
    return [types.TextContent(type="text", text=result)]


def _dispatch(name, args):
    handlers = {
        "trace_create_node": _trace_create_node,
        "trace_create_edge": _trace_create_edge,
        "trace_next_id": _trace_next_id,
        "trace_query": _trace_query,
        "trace_validate": _trace_validate,
        "trace_stats": _trace_stats,
        "trace_report": _trace_report,
        "trace_timeline": _trace_timeline,
        "trace_update_node": _trace_update_node,
        "gate_check": _gate_check,
        "sync_all": _sync_all,
        "state_read": _state_read,
        "state_advance": _state_advance,
        "config_read": _config_read,
        "memory_read": _memory_read,
        "memory_update": _memory_update,
    }
    handler = handlers.get(name)
    if not handler:
        return fail("UNKNOWN_TOOL", message=f"Tool {name} not found")
    return handler(args)


def _trace_create_node(args):
    id_ = args.get("id", "")
    type_ = args.get("type", "")
    title = args.get("title", "")
    traces_from = args.get("traces_from", [])
    status = args.get("status", "draft")
    phase = args.get("phase")
    commit_hash = args.get("commit_hash")
    files_changed = args.get("files_changed", [])
    summary = args.get("summary", "")

    prefix = TYPE_MAP.get(type_)
    if prefix and not id_.startswith(prefix):
        return fail("INVALID_ID_FORMAT", message=f"ID '{id_}' should start with {prefix}",
                    fix=f"Use format {prefix}-NNN")

    conn = get_db()
    if conn is None:
        return fail("NO_DATABASE", fix="Run: python scripts/setup-layer1.py")

    try:
        if conn.execute("SELECT id FROM trace_nodes WHERE id=?", (id_,)).fetchone():
            return fail("DUPLICATE_ID", message=f"Node {id_} already exists",
                        fix="Use trace_next_id to get next available number")
        missing = [r for r in traces_from
                   if not conn.execute("SELECT id FROM trace_nodes WHERE id=?", (r,)).fetchone()]
        if missing:
            return fail("BROKEN_REFERENCE", message=f"Upstream nodes not found: {missing}",
                        fix="Create upstream nodes first")
        now = datetime.now().isoformat()
        metadata = json.dumps({"files_changed": files_changed, "summary": summary}, ensure_ascii=False) if (files_changed or summary) else None
        conn.execute(
            "INSERT INTO trace_nodes (id,type,title,status,phase,commit_hash,metadata,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (id_, type_, title, status, phase, commit_hash, metadata, now, now))
        for ref in traces_from:
            conn.execute(
                "INSERT OR IGNORE INTO trace_edges (from_id,to_id,relation,created_at) VALUES (?,?,?,?)",
                (ref, id_, "traces_to", now))
        conn.commit()
        return ok(node_id=id_, message=f"Node {id_} created", files_tracked=len(files_changed))
    except Exception as e:
        return fail("INTERNAL", message=str(e))
    finally:
        conn.close()


def _trace_create_edge(args):
    from_id = args.get("from_id", "")
    to_id = args.get("to_id", "")
    relation = args.get("relation", "traces_to")
    note = args.get("note", "")
    conn = get_db()
    if conn is None:
        return fail("NO_DATABASE")
    try:
        for nid in [from_id, to_id]:
            if not conn.execute("SELECT id FROM trace_nodes WHERE id=?", (nid,)).fetchone():
                return fail("NODE_NOT_FOUND", message=f"Node {nid} does not exist")
        now = datetime.now().isoformat()
        conn.execute(
            "INSERT OR IGNORE INTO trace_edges (from_id,to_id,relation,note,created_at) VALUES (?,?,?,?,?)",
            (from_id, to_id, relation, note, now))
        conn.commit()
        return ok(from_id=from_id, to_id=to_id, relation=relation)
    except Exception as e:
        return fail("INTERNAL", message=str(e))
    finally:
        conn.close()


def _trace_next_id(args):
    type_ = args.get("type", "")
    prefix = TYPE_MAP.get(type_)
    if not prefix:
        return fail("INVALID_TYPE", message=f"Unknown type: {type_}", valid_types=list(TYPE_MAP.keys()))
    conn = get_db()
    if conn is None:
        return fail("NO_DATABASE", fix="Run: python scripts/setup-layer1.py")
    try:
        row = conn.execute(
            "SELECT id FROM trace_nodes WHERE type=? ORDER BY id DESC LIMIT 1", (type_,)
        ).fetchone()
        max_n = 0
        if row:
            num_str = row["id"].replace(prefix + "-", "")
            if num_str.isdigit():
                max_n = int(num_str)
        next_n = max_n + 1
        total = conn.execute("SELECT COUNT(*) as c FROM trace_nodes WHERE type=?", (type_,)).fetchone()["c"]
        return ok(next_id=f"{prefix}-{next_n:03d}", type=type_, existing_count=total)
    except Exception as e:
        return fail("INTERNAL", message=str(e))
    finally:
        conn.close()


def _trace_query(args):
    direction = args.get("direction", "upstream")
    node_id = args.get("node_id", "")
    conn = get_db()
    if conn is None:
        return fail("NO_DATABASE")
    fname = "trace-upstream.sql" if direction == "upstream" else "trace-downstream.sql"
    sql_path = os.path.join(HARNESS_DIR, ".scaffold", "sql", "queries", fname)
    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read().replace(":node_id", f"'{node_id}'")
    try:
        rows = conn.execute(sql).fetchall()
        return ok(results=[dict(r) for r in rows], count=len(rows))
    except Exception as e:
        return fail("INTERNAL", message=str(e))
    finally:
        conn.close()


def _trace_validate(_args):
    conn = get_db()
    if conn is None:
        return fail("NO_DATABASE")
    sql_path = os.path.join(HARNESS_DIR, ".scaffold", "sql", "queries", "trace-completeness.sql")
    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()
    try:
        rows = conn.execute(sql).fetchall()
        issues = [dict(r) for r in rows]
        return ok(valid=len(issues) == 0, issues=issues, issue_count=len(issues))
    except Exception as e:
        return fail("INTERNAL", message=str(e))
    finally:
        conn.close()


def _trace_stats(_args):
    conn = get_db()
    if conn is None:
        return fail("NO_DATABASE")
    try:
        rows = conn.execute(
            "SELECT type, status, COUNT(*) as count FROM trace_nodes GROUP BY type, status ORDER BY type, status"
        ).fetchall()
        stats = {}
        for r in rows:
            stats.setdefault(r["type"], {})[r["status"]] = r["count"]
        return ok(stats=stats)
    except Exception as e:
        return fail("INTERNAL", message=str(e))
    finally:
        conn.close()


def _trace_report(args):
    node_id = args.get("node_id", "")
    conn = get_db()
    if conn is None:
        return fail("NO_DATABASE")
    try:
        node = conn.execute("SELECT * FROM trace_nodes WHERE id=?", (node_id,)).fetchone()
        if not node:
            return fail("NODE_NOT_FOUND", message=f"Node {node_id} does not exist")
        report = {"node": dict(node)}
        if report["node"].get("metadata"):
            try:
                report["node"]["metadata_parsed"] = json.loads(report["node"]["metadata"])
            except Exception:
                pass
        upstream_fname = "trace-upstream.sql"
        downstream_fname = "trace-downstream.sql"
        for key, fname in [("upstream_chain", upstream_fname), ("downstream_chain", downstream_fname)]:
            sql_path = os.path.join(HARNESS_DIR, ".scaffold", "sql", "queries", fname)
            with open(sql_path, "r", encoding="utf-8") as f:
                sql = f.read().replace(":node_id", f"'{node_id}'")
            rows = conn.execute(sql).fetchall()
            report[key] = [dict(r) for r in rows]
            report[f"{key}_count"] = len(rows)
        report["total_chain_length"] = report["upstream_chain_count"] + report["downstream_chain_count"] + 1
        return ok(report=report)
    except Exception as e:
        return fail("INTERNAL", message=str(e))
    finally:
        conn.close()


def _trace_timeline(args):
    root_id = args.get("root_id", "")
    conn = get_db()
    if conn is None:
        return fail("NO_DATABASE")
    try:
        root = conn.execute("SELECT * FROM trace_nodes WHERE id=?", (root_id,)).fetchone()
        if not root:
            return fail("NODE_NOT_FOUND", message=f"Node {root_id} does not exist")

        impl_types = ("implementation", "fix", "optimization")
        visited = set()
        timeline = []

        def collect_downstream(node_id, depth):
            if node_id in visited:
                return
            visited.add(node_id)
            rows = conn.execute(
                "SELECT to_id FROM trace_edges WHERE from_id=? AND relation='traces_to'", (node_id,)
            ).fetchall()
            for r in rows:
                child = conn.execute("SELECT * FROM trace_nodes WHERE id=?", (r["to_id"],)).fetchone()
                if not child:
                    continue
                meta = None
                if child["metadata"]:
                    try:
                        meta = json.loads(child["metadata"])
                    except Exception:
                        pass
                entry = {
                    "id": child["id"], "type": child["type"], "title": child["title"],
                    "status": child["status"], "commit_hash": child["commit_hash"],
                    "depth": depth, "files_changed": meta.get("files_changed", []) if meta else [],
                    "summary": meta.get("summary", "") if meta else "",
                    "created_at": child["created_at"]
                }
                if child["type"] in impl_types:
                    timeline.append(entry)
                collect_downstream(child["id"], depth + 1)

        collect_downstream(root_id, 0)

        root_meta = None
        if root["metadata"]:
            try:
                root_meta = json.loads(root["metadata"])
            except Exception:
                pass

        return ok(
            root={"id": root["id"], "type": root["type"], "title": root["title"], "status": root["status"]},
            timeline=timeline,
            total_implementations=len(timeline),
            types_breakdown={t: sum(1 for e in timeline if e["type"] == t) for t in impl_types}
        )
    except Exception as e:
        return fail("INTERNAL", message=str(e))
    finally:
        conn.close()


def _trace_update_node(args):
    node_id = args.get("node_id", "")
    new_status = args.get("status")
    new_title = args.get("title")
    new_phase = args.get("phase")
    new_commit_hash = args.get("commit_hash")
    new_files_changed = args.get("files_changed")
    new_summary = args.get("summary")

    if not any([new_status, new_title, new_phase, new_commit_hash, new_files_changed, new_summary]):
        return fail("NO_UPDATE", message="Provide at least one field to update (status, title, phase, commit_hash, files_changed, summary)")

    conn = get_db()
    if conn is None:
        return fail("NO_DATABASE")
    try:
        node = conn.execute("SELECT * FROM trace_nodes WHERE id=?", (node_id,)).fetchone()
        if not node:
            return fail("NODE_NOT_FOUND", message=f"Node {node_id} does not exist")

        valid_transitions = {
            "draft": ["in_progress", "done", "accepted"],
            "in_progress": ["done", "accepted", "draft"],
            "done": ["accepted", "in_progress"],
            "accepted": ["done"],
            "completed": ["done", "accepted"],
        }
        if new_status and new_status != node["status"]:
            allowed = valid_transitions.get(node["status"], [])
            if allowed and new_status not in allowed:
                return fail("INVALID_TRANSITION",
                            message=f"Cannot transition {node_id} from '{node['status']}' to '{new_status}'",
                            allowed_transitions=allowed)

        updates = []
        params = []
        if new_status:
            updates.append("status=?")
            params.append(new_status)
        if new_title:
            updates.append("title=?")
            params.append(new_title)
        if new_phase:
            updates.append("phase=?")
            params.append(new_phase)
        if new_commit_hash:
            updates.append("commit_hash=?")
            params.append(new_commit_hash)

        if new_files_changed or new_summary:
            meta = {}
            if node["metadata"]:
                try:
                    meta = json.loads(node["metadata"])
                except Exception:
                    pass
            if new_files_changed:
                meta["files_changed"] = new_files_changed
            if new_summary:
                meta["summary"] = new_summary
            updates.append("metadata=?")
            params.append(json.dumps(meta, ensure_ascii=False))

        updates.append("updated_at=?")
        params.append(datetime.now().isoformat())
        params.append(node_id)

        conn.execute(f"UPDATE trace_nodes SET {', '.join(updates)} WHERE id=?", params)
        conn.commit()
        return ok(node_id=node_id, updated_fields=[k for k in args.keys() if k != "node_id"])
    except Exception as e:
        return fail("INTERNAL", message=str(e))
    finally:
        conn.close()


def _gate_check(args):
    phase = args.get("phase")
    state_path = os.path.join(CONTROL_DIR, "state.json")
    if not phase:
        if os.path.exists(state_path):
            with open(state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            phase = state.get("current_phase", "")
        if not phase:
            return fail("NO_PHASE", message="No phase specified and no current phase in state.json")

    checks = []
    conn = get_db()
    if conn is None:
        return fail("NO_DATABASE")

    try:
        completeness_path = os.path.join(HARNESS_DIR, ".scaffold", "sql", "queries", "trace-completeness.sql")
        with open(completeness_path, "r", encoding="utf-8") as f:
            sql = f.read()
        broken = conn.execute(sql).fetchall()
        checks.append({
            "name": "trace_completeness",
            "description": "All trace chains should be complete (no broken links)",
            "passed": len(broken) == 0,
            "details": [dict(r) for r in broken] if broken else "All chains complete"
        })

        req_count = conn.execute("SELECT COUNT(*) as c FROM trace_nodes WHERE type='requirement'").fetchone()["c"]
        req_traced = conn.execute(
            "SELECT COUNT(DISTINCT n.id) as c FROM trace_nodes n "
            "JOIN trace_edges e ON e.from_id=n.id WHERE n.type='requirement' AND e.relation='traces_to'"
        ).fetchone()["c"]
        checks.append({
            "name": "requirements_traced",
            "description": "All requirements have downstream trace edges",
            "passed": req_count == 0 or req_traced == req_count,
            "details": f"{req_traced}/{req_count} requirements traced"
        })

        req_ids = [r["id"] for r in conn.execute("SELECT id FROM trace_nodes WHERE type='requirement'").fetchall()]
        req_with_impl = 0
        for rid in req_ids:
            impl = conn.execute(
                "WITH RECURSIVE ds(node_id) AS (SELECT to_id FROM trace_edges WHERE from_id=? "
                "UNION ALL SELECT e.to_id FROM trace_edges e JOIN ds d ON e.from_id=d.node_id) "
                "SELECT 1 FROM ds JOIN trace_nodes t ON t.id=ds.node_id "
                "WHERE t.type IN ('implementation','fix','optimization') LIMIT 1", (rid,)
            ).fetchone()
            if impl:
                req_with_impl += 1
        checks.append({
            "name": "requirements_implemented",
            "description": "All requirements have at least one downstream implementation",
            "passed": req_count == 0 or req_with_impl == req_count,
            "details": f"{req_with_impl}/{req_count} requirements have implementations"
        })

        tsk_count = conn.execute("SELECT COUNT(*) as c FROM trace_nodes WHERE type='task'").fetchone()["c"]
        tsk_done = conn.execute("SELECT COUNT(*) as c FROM trace_nodes WHERE type='task' AND status IN ('done','completed')").fetchone()["c"]
        checks.append({
            "name": "tasks_completion",
            "description": "All tasks should be done (info only, not blocking)",
            "passed": tsk_count == 0 or tsk_done == tsk_count,
            "details": f"{tsk_done}/{tsk_count} tasks done"
        })

        phase_gates = {
            "scaffold": ["trace_completeness"],
            "implement": ["trace_completeness", "requirements_traced", "requirements_implemented"],
            "verify": ["trace_completeness", "requirements_implemented", "tasks_completion"],
            "acceptance": ["trace_completeness", "requirements_implemented", "tasks_completion"],
        }
        relevant = phase_gates.get(phase, ["trace_completeness", "requirements_traced"])
        gate_results = [c for c in checks if c["name"] in relevant]
        blocking = [c for c in gate_results if not c["passed"]]

        return ok(
            phase=phase,
            gate_passed=len(blocking) == 0,
            checks=checks,
            relevant_gates=relevant,
            blocking=[c["name"] for c in blocking],
            can_advance=len(blocking) == 0
        )
    except Exception as e:
        return fail("INTERNAL", message=str(e))
    finally:
        conn.close()


def _sync_knowledge_status(conn):
    results = []
    rows = conn.execute("SELECT id, type, status FROM trace_nodes").fetchall()
    for row in rows:
        dir_name = TYPE_DIR_MAP.get(row["type"])
        if not dir_name:
            continue
        pattern = os.path.join(KNOWLEDGE_DIR, dir_name, f"{row['id']}*.md")
        matches = glob.glob(pattern)
        if not matches:
            results.append({"id": row["id"], "action": "skip", "reason": "no .md file"})
            continue
        for fpath in matches:
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                new_content = re.sub(
                    r"^status:\s*\S+", f"status: {row['status']}",
                    content, count=1, flags=re.MULTILINE
                )
                if new_content != content:
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    results.append({"id": row["id"], "action": "updated", "file": os.path.basename(fpath)})
                else:
                    results.append({"id": row["id"], "action": "unchanged", "file": os.path.basename(fpath)})
            except Exception as e:
                results.append({"id": row["id"], "action": "error", "error": str(e)})
    return results


def _sync_state_json(conn):
    state_path = os.path.join(CONTROL_DIR, "state.json")
    if not os.path.exists(state_path):
        return {"action": "skip", "reason": "state.json not found"}
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
        rows = conn.execute(
            "SELECT DISTINCT type FROM trace_nodes WHERE status='done'"
        ).fetchall()
        done_types = [r["type"] for r in rows]
        total = conn.execute("SELECT COUNT(*) as c FROM trace_nodes").fetchone()["c"]
        done = conn.execute("SELECT COUNT(*) as c FROM trace_nodes WHERE status IN ('done','completed','accepted')").fetchone()["c"]
        state["trace_summary"] = {"total_nodes": total, "done_nodes": done, "done_types": done_types}

        current_phase = state.get("current_phase", "")
        if current_phase and current_phase in state.get("phases", {}):
            phase_info = state["phases"][current_phase]
            tasks = conn.execute(
                "SELECT id, title, commit_hash FROM trace_nodes WHERE type='task' AND status='done' ORDER BY created_at"
            ).fetchall()
            impls = conn.execute(
                "SELECT id, title, commit_hash FROM trace_nodes "
                "WHERE type IN ('implementation','fix','optimization') AND status='done' ORDER BY created_at"
            ).fetchall()
            completed = []
            for t in tasks:
                desc = f"{t['id']}: {t['title']}"
                if t["commit_hash"]:
                    desc += f" — commit {t['commit_hash'][:7]}"
                completed.append(desc)
            for imp in impls:
                desc = f"{imp['id']}: {imp['title']}"
                if imp["commit_hash"]:
                    desc += f" — commit {imp['commit_hash'][:7]}"
                completed.append(desc)
            phase_info["completed_tasks"] = completed

        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        return {"action": "updated", "total": total, "done": done}
    except Exception as e:
        return {"action": "error", "error": str(e)}


def _sync_harness_summary(conn):
    summary_path = os.path.join(CONTROL_DIR, "harness.summary.md")
    try:
        state_path = os.path.join(CONTROL_DIR, "state.json")
        phase = "unknown"
        if os.path.exists(state_path):
            with open(state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            phase = state.get("current_phase", "unknown")
        stats_rows = conn.execute(
            "SELECT type, status, COUNT(*) as count FROM trace_nodes GROUP BY type, status"
        ).fetchall()
        stats = {}
        for r in stats_rows:
            stats.setdefault(r["type"], {})[r["status"]] = r["count"]
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = [
            f"# Harness Summary",
            f"",
            f"Generated: {now_str}",
            f"Phase: {phase}",
            f"",
            f"## Trace Stats",
            f"",
        ]
        for type_, statuses in sorted(stats.items()):
            parts = [f"{s}:{c}" for s, c in sorted(statuses.items())]
            lines.append(f"- **{type_}**: {', '.join(parts)}")
        content = "\n".join(lines) + "\n"
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"action": "updated"}
    except Exception as e:
        return {"action": "error", "error": str(e)}


def _sync_compensate_status(conn):
    rows = conn.execute(
        "SELECT id, type, status, commit_hash FROM trace_nodes WHERE commit_hash IS NOT NULL AND status='draft'"
    ).fetchall()
    compensated = []
    for row in rows:
        conn.execute("UPDATE trace_nodes SET status='done', updated_at=? WHERE id=?",
                     (datetime.now().isoformat(), row["id"]))
        compensated.append({"id": row["id"], "type": row["type"], "previous_status": "draft", "new_status": "done"})
    if compensated:
        conn.commit()
    return compensated


def _sync_all(args):
    conn = get_db()
    if conn is None:
        return fail("NO_DATABASE")

    report = {"steps": [], "errors": []}

    try:
        compensated = _sync_compensate_status(conn)
        report["steps"].append({
            "step": "0. status compensation (draft with commit → done)",
            "result": {"compensated": compensated, "count": len(compensated)}
        })
    except Exception as e:
        report["errors"].append({"step": "compensate_status", "error": str(e)})

    try:
        report["steps"].append({
            "step": "1. knowledge .md status sync",
            "result": _sync_knowledge_status(conn)
        })
    except Exception as e:
        report["errors"].append({"step": "knowledge_sync", "error": str(e)})

    try:
        report["steps"].append({
            "step": "2. state.json milestone sync",
            "result": _sync_state_json(conn)
        })
    except Exception as e:
        report["errors"].append({"step": "state_sync", "error": str(e)})

    try:
        report["steps"].append({
            "step": "3. harness.summary.md regenerate",
            "result": _sync_harness_summary(conn)
        })
    except Exception as e:
        report["errors"].append({"step": "summary_regen", "error": str(e)})

    active_context = args.get("active_context")
    if active_context:
        try:
            path = os.path.join(CONTROL_DIR, "memory-bank", "activeContext.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(active_context)
            report["steps"].append({"step": "4. activeContext.md update", "result": {"action": "updated"}})
        except Exception as e:
            report["errors"].append({"step": "active_context", "error": str(e)})

    progress_entry = args.get("progress_entry")
    if progress_entry:
        try:
            path = os.path.join(CONTROL_DIR, "memory-bank", "progress.md")
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"\n{progress_entry}")
            report["steps"].append({"step": "5. progress.md append", "result": {"action": "appended"}})
        except Exception as e:
            report["errors"].append({"step": "progress", "error": str(e)})

    conn.close()
    success = len(report["errors"]) == 0
    report["success"] = success
    report["message"] = "All steps completed" if success else f"{len(report['errors'])} error(s) occurred"
    return json.dumps(report, ensure_ascii=False, indent=2)


def _state_read(_args):
    path = os.path.join(CONTROL_DIR, "state.json")
    if not os.path.exists(path):
        return fail("NO_STATE_FILE", fix="Copy templates/_blank/state.json to .control/")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _state_advance(args):
    phase_name = args.get("phase_name", "")
    validation_log = args.get("validation_log", "")
    skip_gate = args.get("skip_gate", False)
    state_path = os.path.join(CONTROL_DIR, "state.json")
    if not os.path.exists(state_path):
        return fail("NO_STATE_FILE")
    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)
    current = state.get("current_phase", "")
    if phase_name == current:
        return fail("ALREADY_IN_PHASE", message=f"Already in phase {phase_name}")

    if not skip_gate and current:
        gate_result = _gate_check({"phase": current})
        try:
            gate_data = json.loads(gate_result)
            if not gate_data.get("success") or not gate_data.get("can_advance", True):
                blocking = gate_data.get("blocking", [])
                return fail("GATE_BLOCKED",
                            message=f"Cannot advance from '{current}': gate checks failed",
                            blocking=blocking,
                            checks=gate_data.get("checks", []),
                            fix="Fix blocking issues or set skip_gate=true")
        except (json.JSONDecodeError, KeyError):
            pass

    now = datetime.now().isoformat()
    if current and current in state.get("phases", {}):
        state["phases"][current]["status"] = "completed"
        state["phases"][current]["completed_at"] = now
        state["phases"][current]["validation_log"] = validation_log
        state.setdefault("completed_phases", [])
        if current not in state["completed_phases"]:
            state["completed_phases"].append(current)
    state.setdefault("phases", {}).setdefault(phase_name, {})
    state["phases"][phase_name]["status"] = "in_progress"
    state["phases"][phase_name]["started_at"] = now
    state["current_phase"] = phase_name
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    return ok(new_phase=phase_name, previous_phase=current)


def _deep_merge(base, override):
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _load_yaml_safe(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    result = {}
    current_section = result
    current_key = None
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith(" ") and not line.startswith("\t") and ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()
            if val:
                current_section[key] = _parse_yaml_value(val)
            else:
                current_section[key] = {}
                current_section = result
                current_key = key
                current_section = result[key]
        elif current_key and stripped:
            pass
    return result


def _parse_yaml_value(val):
    if val.lower() in ("true", "yes"):
        return True
    if val.lower() in ("false", "no"):
        return False
    if val.isdigit():
        return int(val)
    try:
        return float(val)
    except ValueError:
        pass
    if val.startswith("[") and val.endswith("]"):
        items = val[1:-1].split(",")
        return [i.strip().strip("\"'") for i in items if i.strip()]
    if val.startswith('"') and val.endswith('"'):
        return val[1:-1]
    return val


def _config_read(_args):
    defaults_path = os.path.join(HARNESS_DIR, ".scaffold", "defaults", "harness-defaults.yml")
    harness_path = os.path.join(CONTROL_DIR, "harness.yml")

    layer1 = _load_yaml_safe(defaults_path)
    layer3 = _load_yaml_safe(harness_path)

    merged = dict(layer1)
    if layer3:
        project = layer3.get("project", {})
        if project:
            merged["project"] = _deep_merge(merged.get("project", {}), project)
        override = layer3.get("override", {})
        if override:
            merged = _deep_merge(merged, override)

    sources = {}
    all_keys = set(list(layer1.keys()) + list(layer3.get("override", {}).keys()))
    for key in all_keys:
        in_override = key in layer3.get("override", {})
        sources[key] = "project_override" if in_override else "framework_default"

    return ok(
        merged=merged,
        sources=sources,
        layers={
            "layer1_framework_default": "loaded" if layer1 else "not_found",
            "layer3_project_override": "loaded" if layer3.get("override") else "none",
        }
    )


def _memory_read(_args):
    result = {}
    for name in ["activeContext", "progress"]:
        path = os.path.join(CONTROL_DIR, "memory-bank", f"{name}.md")
        result[name] = open(path, "r", encoding="utf-8").read() if os.path.exists(path) else None
    return ok(files=result)


def _memory_update(args):
    file_name = args.get("file_name", "")
    content = args.get("content", "")
    if file_name not in ["activeContext", "progress"]:
        return fail("INVALID_FILE", message="file_name must be 'activeContext' or 'progress'")
    path = os.path.join(CONTROL_DIR, "memory-bank", f"{file_name}.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return ok(file=file_name, path=f"memory-bank/{file_name}.md")


async def main():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
