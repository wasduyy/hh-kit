# Git 约定

## Commit Message 格式

```
[{追溯ID}|{任务ID}|{上游追溯}] {标题}

{详细说明}

Traces: {上游追溯ID, 逗号分隔}
```

### 格式解析

- `追溯ID`: 本次提交的追溯标识（如 IMP-012、BUG-003）
- `任务ID`: 对应的任务标识（如 TSK-007）
- `上游追溯`: 完整的因果链（如 DEC-003,REQ-001）

### 示例

```
[REQ-001] 定义需求：多源异构数据统一接入
Traces: (需求为源头，无上游)

[ANA-001] 数据源类型与存储需求调研完成
Traces: REQ-001

[DEC-003] 双存储引擎选型：Neo4j + Qdrant
Traces: ANA-001, REQ-001

[TSK-007] 创建任务：实现 Qdrant 向量存储客户端
Traces: DEC-003, REQ-001

[IMP-012|TSK-007] 实现 vector_store.py
Traces: TSK-007, DEC-003, REQ-001

[TST-015|TSK-007] Qdrant 向量存储单元测试
Traces: IMP-012, TSK-007

[BUG-003] 发现 Qdrant 连接池泄漏
Traces: TST-015, IMP-012

[IMP-018|BUG-003] 修复连接池泄漏
Traces: BUG-003, IMP-012, REQ-001
```

## 分支命名约定

```
{领域代码小写}/{追溯ID}-{简短描述}

req/REQ-001-multi-source-ingestion
ana/ANA-001-storage-research
dec/DEC-003-dual-storage
tsk/TSK-007-qdrant-client
fix/BUG-003-conn-pool-leak
rev/REV-001-sprint-1-review
```

## 领域代码对照

| 代码 | 领域 | 分支前缀 |
|------|------|---------|
| REQ | 需求 | req/ |
| ANA | 分析 | ana/ |
| DEC | 决策 | dec/ |
| TSK | 任务 | tsk/ |
| IMP | 工程实现 | imp/ |
| TST | 测试 | tst/ |
| BUG | 缺陷 | fix/ |
| REV | 回顾 | rev/ |
