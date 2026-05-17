# T-004: Phase Advance Blocked

## Symptom
`state_advance` returns an error, or the Skill indicates the phase cannot advance.

## Cause
One or more gate conditions are not met. Common gates:
- `unit_tests_pass`: Tests are failing
- `integration_tests_pass`: Integration tests are failing
- `coverage >= 80`: Code coverage is too low
- `requirements_traced`: Requirements lack downstream decisions
- `acceptance_report_all_pass`: Acceptance tests are failing

## Solution

### Check which gates are failing
If using MCP: call `gate_check(phase_name)` to get detailed results.

### Manual check
1. Read the phase definition in `harness.yml` to see gate requirements
2. Run the required tests or checks manually
3. Fix any failures
4. Retry the phase advance

### Skip a gate (not recommended)
If a gate is not applicable to your project, override the phase definition in `harness.yml`:
```yaml
override:
  phases:
    - name: verify
      gates: ["unit_tests_pass"]
```
