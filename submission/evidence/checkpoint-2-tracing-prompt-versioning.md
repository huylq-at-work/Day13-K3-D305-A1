# Checkpoint 2 - Role 2 Tracing & Prompt Versioning

Owner: Liên - Role 2

## Langfuse prompt

- Prompt name: `day13-chat`
- Prompt contract:

```text
Feature={{feature}}
Docs={{docs}}
Question={{message}}
```

## Prompt versions and labels

- Version 1: labels `baseline`, `production`
- Version 2: label `candidate`
- Label switch verified: `production` was moved to version 2.
- Rollback verified: `production` was moved back to version 1.

## Trace evidence

All traces below have metadata `prompt_name=day13-chat`, `prompt_source=langfuse`, and the listed `prompt_label` / `prompt_version`.

| Label | Version | Session | Trace ID | Trace URL |
|---|---:|---|---|---|
| baseline | 1 | `cp2-role2-lien-baseline` | `7e89ea3111f42b814ad5b735b07d2f5f` | https://cloud.langfuse.com/project/cmso2hxp603n5ad0iwizl6duk/traces/7e89ea3111f42b814ad5b735b07d2f5f |
| baseline | 1 | `cp2-role2-lien-baseline` | `62c1d62f9fa680cb0414590bfc77bcfb` | https://cloud.langfuse.com/project/cmso2hxp603n5ad0iwizl6duk/traces/62c1d62f9fa680cb0414590bfc77bcfb |
| baseline | 1 | `cp2-role2-lien-baseline` | `4e16aec0b8c0e80889371bfe349ea7de` | https://cloud.langfuse.com/project/cmso2hxp603n5ad0iwizl6duk/traces/4e16aec0b8c0e80889371bfe349ea7de |
| baseline | 1 | `cp2-role2-lien-baseline` | `3a2e492219342dcdbf3f5eea3171bb15` | https://cloud.langfuse.com/project/cmso2hxp603n5ad0iwizl6duk/traces/3a2e492219342dcdbf3f5eea3171bb15 |
| candidate | 2 | `cp2-role2-lien-candidate` | `fc60baea1602e9759d9807b9bcd15a01` | https://cloud.langfuse.com/project/cmso2hxp603n5ad0iwizl6duk/traces/fc60baea1602e9759d9807b9bcd15a01 |
| candidate | 2 | `cp2-role2-lien-candidate` | `41b5857fa140eeec5ad2ca4c018bae68` | https://cloud.langfuse.com/project/cmso2hxp603n5ad0iwizl6duk/traces/41b5857fa140eeec5ad2ca4c018bae68 |
| candidate | 2 | `cp2-role2-lien-candidate` | `9d5a84f41e5ca39807f71073a36947f6` | https://cloud.langfuse.com/project/cmso2hxp603n5ad0iwizl6duk/traces/9d5a84f41e5ca39807f71073a36947f6 |
| candidate | 2 | `cp2-role2-lien-candidate` | `c067ec6aa422be2e7d63a72d5c283d09` | https://cloud.langfuse.com/project/cmso2hxp603n5ad0iwizl6duk/traces/c067ec6aa422be2e7d63a72d5c283d09 |
| production | 1 | `cp2-role2-lien-production-rollback` | `bd16ddb65d4569681c162a85717e1023` | https://cloud.langfuse.com/project/cmso2hxp603n5ad0iwizl6duk/traces/bd16ddb65d4569681c162a85717e1023 |
| production | 1 | `cp2-role2-lien-production-rollback` | `99502f418661e53e6f8181e9ff7cabac` | https://cloud.langfuse.com/project/cmso2hxp603n5ad0iwizl6duk/traces/99502f418661e53e6f8181e9ff7cabac |

## Notable span

The `run` generation span links the generated answer to the managed prompt. Its metadata includes `doc_count`, `query_preview`, `prompt_name`, `prompt_label`, `prompt_version`, and `prompt_source`, which lets the team explain which prompt version produced each answer and safely verify rollback behavior.
