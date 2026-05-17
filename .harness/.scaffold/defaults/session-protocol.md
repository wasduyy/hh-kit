# 会话协议

## 会话开始

1. 读取 `.control/state.json` → 获取当前阶段
2. 读取 `memory-bank/activeContext.md` → 获取当前焦点
3. 读取 `harness.summary.md` → 了解当前配置概况
4. 向用户汇报：

```
项目: {project_name}
Starter: {starter_name}
阶段: {current_phase} ({phase_status})
上次工作: {active_context_summary}
配置覆盖: {override_summary, 如果有}
```

5. 基于当前阶段和焦点，开始工作

## 会话结束

1. 更新 `memory-bank/activeContext.md`：
   - 当前焦点（正在做什么）
   - 未完成事项
   - 遇到的问题
   - 下次应该从哪里继续

2. 更新 `memory-bank/progress.md`：
   - 本次会话完成了什么
   - 创建了哪些追溯节点
   - 变更了哪些文件

3. 如果完成了阶段的关键任务，提示用户是否推进阶段
