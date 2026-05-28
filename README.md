# think-condenser

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Cursor Agent Skill — 压缩 AI 内部思考与冗长文本，去除 meta/过渡/重复，保留关键词与决策信息，节省 token 且不降低任务质量。

## 特性

- **Live Thinking** — Agent 推理时自动精简（无需脚本）
- **Script Batch** — CLI 批量压缩日志 / prompt / 思考记录
- **双语** — 中英文 meta 词、过渡词、重复句
- **质量保护** — 路径、错误、否定词、条件分支不压缩

## 快速安装

### TRAE SOLO（比赛推荐）

```bash
git clone https://github.com/JinHao-stu/condenser_skills.git
mkdir -p .trae/skills
cp -R condenser_skills .trae/skills/think-condenser
```

重启或刷新 TRAE Agent，在「规则技能」中确认 `think-condenser` 已加载。

### Cursor（个人全局）

```bash
git clone https://github.com/JinHao-stu/condenser_skills.git
mkdir -p ~/.cursor/skills
cp -R condenser_skills ~/.cursor/skills/think-condenser
```

重启 Cursor，或在对话中 `@think-condenser` 引用。

### Cursor（仅当前项目）

```bash
mkdir -p .cursor/skills
cp -R /path/to/think-condenser .cursor/skills/think-condenser
```

### Skills CLI

```bash
npx skills add <owner>/think-condenser -g -y
```

## 脚本用法（可选）

**Quick 模式**（无依赖，推荐先试）：

```bash
python scripts/condense.py --quick --stats -i reasoning.txt
```

**Full 模式**（spaCy NLP，更高质量去重）：

```bash
python3 -m pip install --upgrade pip
pip install -r scripts/requirements.txt
python -m spacy download zh_core_web_sm en_core_web_sm
python scripts/condense.py -i reasoning.txt --stats
```

> 系统 Python 3.9 需先升级 pip；若安装仍失败，请用 Python 3.10+ 或继续用 `--quick` 模式。

**运行测试**：

```bash
python scripts/run_tests.py
```

## 目录结构

```
think-condenser/
├── SKILL.md           # Agent 主指令（必需）
├── README.md          # 本文件
├── LICENSE
├── CHANGELOG.md
├── examples.md        # 压缩前后示例
├── reference.md       # 管道与 API 参考
├── .gitignore
└── scripts/
    ├── condense.py        # CLI 入口
    ├── condenser.py       # spaCy 完整版
    ├── quick_condense.py  # 正则快速版
    ├── run_tests.py       # 测试套件
    └── requirements.txt
```

## 压缩强度

| 预设 | 说明 |
|------|------|
| `light` | 仅去 meta / 过渡词 |
| `balanced` | 默认，平衡压缩与保真 |
| `aggressive` | 最大压缩，仍保留标识符 |

## 发布指南

1. 将本仓库推送到 GitHub（仓库名建议 `think-condenser`）
2. 确保根目录包含 `SKILL.md`（Skills 规范要求）
3. 打 tag 发布版本：`git tag v1.0.0 && git push origin v1.0.0`
4. 可选：提交到 [skills.sh](https://skills.sh/) 生态

```bash
git init
git add .
git commit -m "release: think-condenser v1.0.0"
git remote add origin git@github.com:<user>/think-condenser.git
git push -u origin main
```

## 文档

- [examples.md](examples.md) — 压缩示例
- [reference.md](reference.md) — API 与管道细节
- [CHANGELOG.md](CHANGELOG.md) — 版本记录

## License

MIT — see [LICENSE](LICENSE)
