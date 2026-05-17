# hh-kit — AI Engineering Scaffold

> **AI Engineering Scaffold — 约定大于配置的 AI 编程工程脚手架**

hh-kit 是一个基于"约定大于配置"理念的 AI 工程脚手架。clone 后直接就是你的工作空间，零配置即可开始工作。

---

## 快速开始

```bash
# 1. 用 hh-kit 初始化你的项目
git clone https://github.com/xxx/hh-kit.git my-project
cd my-project

# 2. （可选）初始化 Python 环境和 MCP Server
powershell -ExecutionPolicy Bypass -File .harness/scripts/init-venv.ps1

# 3. （可选）初始化 SQLite 追溯库 + Git hooks
python .harness/scripts/setup-layer1.py

# 4. 打开你的 AI IDE，开始工作
```

**零配置模式**：如果不运行任何脚本，hh-kit 同样完整可用——只是追溯需要手动管理。

---

## 核心理念

| 原则 | 说明 |
|------|------|
| 约定大于配置 | 不配置就走约定，需要覆盖时在 `harness.yml` 显式声明 |
| 分层可用 | 零依赖也能用，装了 MCP 更好 |
| DB 是真相源 | SQLite 追溯库是工程状态的唯一权威来源 |
| 可审计可追溯 | 所有工程事件的因果链完整记录 |

---

## 工作空间结构

```
hh-kit/                 ← 你的项目工作空间
├── .harness/                   ← 框架内核（通常不改）
│   ├── .scaffold/              约定、配置、MCP Server、SQL、hooks
│   ├── skills/                 8 个 Skills（行为指导）
│   ├── personas/               角色定义
│   ├── scripts/                工具脚本
│   ├── templates/              Starter 模板
│   └── troubleshooting/        故障手册
├── .control/                   ← 工程控制（状态、配置、记忆）
│   ├── harness.yml             项目配置（唯一入口）
│   ├── state.json              当前阶段状态
│   └── memory-bank/            会话记忆
├── knowledge/                  ← 过程资产（需求、决策、追溯）
├── project/                    ← 开发产物（源代码、测试）
└── .trae/                      ← Trae IDE 适配器
```

---

## MCP 工具（15 个）

| 工具 | 功能 |
|------|------|
| trace_create_node | 创建追溯节点 |
| trace_create_edge | 创建追溯关系 |
| trace_next_id | 获取下一个可用 ID |
| trace_query | 查询追溯图（上游/下游） |
| trace_validate | 验证追溯链完整性 |
| trace_stats | 追溯统计 |
| trace_report | 节点完整追溯报告 |
| trace_timeline | 实现时间线 |
| trace_update_node | 更新节点状态 |
| gate_check | 门禁检查 |
| sync_all | 全量状态同步 |
| state_read | 读取阶段状态 |
| state_advance | 推进阶段（含门禁） |
| config_read | 三层配置合并读取 |
| memory_read / memory_update | 会话记忆管理 |

---

## Skills（8 个）

| Skill | 类型 | 说明 |
|-------|------|------|
| session-start | 流程型 | 会话开始：恢复上下文 |
| session-end | 流程型 | 会话结束：持久化状态 |
| trace-create | 流程型 | 创建追溯节点 |
| stage-advance | 流程型 | 阶段推进：门禁→确认→推进 |
| code-review | 框架型 | 代码审查：6 维度评估 |
| bug-fix | 流程型 | BUG→FIX 完整闭环 |
| research-and-plan | 混合型 | 研究→分析→决策→任务 |
| adr-write | 框架型 | 架构决策记录 |

---

## 追溯链

```
REQ(需求) → ANA(分析) → DEC(决策) → TSK(任务)
  → IMP(实现) → TST(测试) → BUG(缺陷) → FIX(修复)
```

每个节点 = SQLite 记录 + 可选 Markdown 文件。支持递归 CTE 图遍历。

---

## 依赖分层

```
Layer 0: Git + AI IDE          → 完整可用
Layer 1: + Python + SQLite     → 自动追溯、门禁、状态管理
Layer 2: + Docker              → 团队协作、Web 看板（规划中）
Layer 3: + 项目管理系统          → 企业级 ALM（规划中）
```

---

## 版本

当前版本：**v0.1.0** — Layer 0 + Layer 1 核心可用

## License

MIT
