# Backend Automated Testing & CI/CD Design

## Context

AIFriends 项目当前没有自动化测试（`backend/web/tests.py` 为空）。需要为 Django 后端建立完整的自动化测试体系，并通过 GitHub Actions 实现 CI 流水线。

## Scope

- 后端测试：Django 模型、API 视图（DRF）、工具函数（混合检索、RRF、BM25）
- CI 平台：GitHub Actions
- 触发方式：push to main、PR、手动触发（workflow_dispatch）
- 数据库：SQLite 内存模式（无需 MySQL）

## Test Framework

- **运行器**: pytest + pytest-django
- **测试类**: Django `TestCase` / DRF `APITestCase`
- **覆盖率**: pytest-cov，生成 xml + html 报告

## Directory Structure

```
backend/
├── pytest.ini                    # pytest 配置
├── web/
│   ├── tests/                    # 测试根目录
│   │   ├── __init__.py
│   │   ├── conftest.py           # 全局 fixtures
│   │   ├── test_models/
│   │   │   ├── __init__.py
│   │   │   ├── test_character.py
│   │   │   ├── test_friend.py
│   │   │   └── test_user.py
│   │   ├── test_views/
│   │   │   ├── __init__.py
│   │   │   ├── test_auth.py
│   │   │   ├── test_character.py
│   │   │   ├── test_friend.py
│   │   │   └── test_chat.py
│   │   └── test_utils/
│   │       ├── __init__.py
│   │       ├── test_hybrid_search.py
│   │       ├── test_rrf.py
│   │       └── test_bm25.py
├── .github/
│   └── workflows/
│       └── test.yml
```

## Test Database Strategy

Django 测试框架自动用 SQLite 内存数据库替换 settings 中的 MySQL。每个 TestCase 事务隔离，自动回滚，无需手动清理。

## What to Test

### Views (API)
| Module | Tests |
|--------|-------|
| test_auth | Register (success / duplicate username), Login (success / wrong password / nonexistent user), Logout, JWT refresh |
| test_character | Create (success / missing fields / unauthorized), Get list, Get single, Update, Delete |
| test_friend | Get or create, Get list, Delete (owner only) |
| test_chat | SSE chat (success / empty message / invalid friend_id), Get message history, ASR |

### Models
| Module | Tests |
|--------|-------|
| test_character | Character.__str__, Voice.__str__, ForeignKey cascade |
| test_friend | Friend.__str__, Message.__str__, SystemPrompt.__str__, auto create_time |
| test_user | UserProfile creation on user create |

### Utils (pure unit tests, no DB)
| Module | Tests |
|--------|-------|
| test_rrf | RRF score calculation, multi-list fusion, edge cases (single/empty list) |
| test_hybrid_search | Result structure, result count limit, empty query handling |
| test_bm25 | BM25 basic search functionality |

## GitHub Actions Workflow

- **runs-on**: ubuntu-latest
- **python-version**: 3.12
- **Steps**: checkout → setup python → install deps → pytest with coverage → upload artifact
- **Artifact**: coverage html report uploaded regardless of pass/fail

## Conftest Fixtures

- `api_client`: DRF APIClient
- `auth_client`: APIClient with `force_authenticate` (JWT bypassed in tests)
- `test_user`: create a test user and UserProfile
- `test_character`: create a test character
- `test_friend`: create a test friend relationship
