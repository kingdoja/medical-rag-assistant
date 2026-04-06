# Git 使用指南

本文档介绍如何将 PathoMind 项目推送到 GitHub。

## 首次推送到GitHub

### 1. 在GitHub上创建仓库

1. 访问 https://github.com
2. 点击右上角的 "+" -> "New repository"
3. 填写仓库信息：
   - Repository name: `pathomind` 或你喜欢的名字
   - Description: "医疗知识与质控助手 - 基于RAG的智能检索系统"
   - 选择 Public 或 Private
   - **不要**勾选 "Initialize this repository with a README"
4. 点击 "Create repository"

### 2. 初始化本地Git仓库

```bash
# 进入项目目录
cd pathomind

# 初始化Git仓库（如果还没有）
git init

# 查看当前状态
git status
```

### 3. 配置Git用户信息（如果还没配置）

```bash
git config --global user.name "你的名字"
git config --global user.email "your.email@example.com"
```

### 4. 添加文件到Git

```bash
# 添加所有文件
git add .

# 查看将要提交的文件
git status

# 如果有不想提交的文件，确保它们在.gitignore中
```

### 5. 创建首次提交

```bash
git commit -m "Initial commit: PathoMind medical knowledge assistant"
```

### 6. 连接到GitHub远程仓库

```bash
# 添加远程仓库（替换为你的GitHub用户名和仓库名）
git remote add origin https://github.com/yourusername/pathomind.git

# 验证远程仓库
git remote -v
```

### 7. 推送到GitHub

```bash
# 推送到main分支
git push -u origin main

# 如果你的默认分支是master，使用：
# git push -u origin master
```

如果遇到认证问题，可能需要：
- 使用Personal Access Token (PAT) 代替密码
- 配置SSH密钥

## 使用Personal Access Token

### 创建PAT

1. 访问 GitHub Settings -> Developer settings -> Personal access tokens -> Tokens (classic)
2. 点击 "Generate new token (classic)"
3. 设置token名称和过期时间
4. 勾选权限：`repo` (完整的仓库访问权限)
5. 点击 "Generate token"
6. **复制token**（只显示一次！）

### 使用PAT推送

```bash
# 方式1: 在URL中使用token
git remote set-url origin https://YOUR_TOKEN@github.com/yourusername/pathomind.git
git push -u origin main

# 方式2: 使用Git凭据管理器
git push -u origin main
# 当提示输入密码时，粘贴你的PAT
```

## 使用SSH密钥（推荐）

### 生成SSH密钥

```bash
# 生成新的SSH密钥
ssh-keygen -t ed25519 -C "your.email@example.com"

# 按Enter使用默认位置
# 可以设置密码或直接按Enter

# 启动ssh-agent
eval "$(ssh-agent -s)"

# 添加SSH密钥
ssh-add ~/.ssh/id_ed25519
```

### 添加SSH密钥到GitHub

```bash
# 复制公钥到剪贴板
# Linux:
cat ~/.ssh/id_ed25519.pub
# Mac:
pbcopy < ~/.ssh/id_ed25519.pub
# Windows (Git Bash):
clip < ~/.ssh/id_ed25519.pub
```

1. 访问 GitHub Settings -> SSH and GPG keys
2. 点击 "New SSH key"
3. 粘贴公钥内容
4. 点击 "Add SSH key"

### 使用SSH URL

```bash
# 更改远程仓库URL为SSH
git remote set-url origin git@github.com:yourusername/pathomind.git

# 推送
git push -u origin main
```

## 日常Git工作流

### 查看状态

```bash
# 查看当前状态
git status

# 查看修改内容
git diff

# 查看提交历史
git log --oneline
```

### 提交更改

```bash
# 添加特定文件
git add file1.py file2.py

# 添加所有修改的文件
git add .

# 提交
git commit -m "feat: add new feature"

# 推送到远程
git push
```

### 拉取更新

```bash
# 拉取远程更新
git pull origin main

# 或者先fetch再merge
git fetch origin
git merge origin/main
```

### 分支管理

```bash
# 创建新分支
git checkout -b feature/new-feature

# 切换分支
git checkout main

# 查看所有分支
git branch -a

# 合并分支
git checkout main
git merge feature/new-feature

# 删除本地分支
git branch -d feature/new-feature

# 删除远程分支
git push origin --delete feature/new-feature
```

## 提交信息规范

使用语义化的提交信息：

```bash
# 新功能
git commit -m "feat: add document grouping feature"

# Bug修复
git commit -m "fix: resolve memory leak in embedding process"

# 文档更新
git commit -m "docs: update deployment guide"

# 代码重构
git commit -m "refactor: simplify query processing logic"

# 性能优化
git commit -m "perf: optimize vector search performance"

# 测试相关
git commit -m "test: add unit tests for reranker"

# 构建/工具相关
git commit -m "chore: update dependencies"
```

## 常见问题

### Q: 推送时提示 "Permission denied"

A: 检查：
1. 远程URL是否正确
2. 是否有仓库的写入权限
3. SSH密钥或PAT是否配置正确

### Q: 推送时提示 "Updates were rejected"

A: 远程有新的提交，需要先拉取：
```bash
git pull origin main --rebase
git push origin main
```

### Q: 不小心提交了敏感信息

A: 立即从历史中删除：
```bash
# 从最后一次提交中删除文件
git rm --cached sensitive_file
git commit --amend -m "Remove sensitive file"
git push --force

# 从整个历史中删除（使用git-filter-repo）
pip install git-filter-repo
git filter-repo --path sensitive_file --invert-paths
git push --force
```

### Q: 想要撤销最后一次提交

A: 
```bash
# 保留更改，撤销提交
git reset --soft HEAD~1

# 丢弃更改，撤销提交
git reset --hard HEAD~1
```

## 推送前检查清单

- [ ] 确保 `.gitignore` 正确配置
- [ ] 删除或忽略敏感信息（API keys, 密码等）
- [ ] 删除或忽略大文件（数据库文件、模型文件等）
- [ ] 运行测试确保代码正常工作
- [ ] 更新 README 和相关文档
- [ ] 检查提交信息是否清晰
- [ ] 确认要推送的分支正确

## 推荐的.gitignore配置

项目已包含完整的 `.gitignore` 文件，主要忽略：

- Python缓存文件 (`__pycache__/`, `*.pyc`)
- 虚拟环境 (`.venv/`, `venv/`)
- 数据文件 (`data/`, `*.db`)
- 日志文件 (`logs/`, `*.log`)
- 配置文件 (`.env`, `config/*local.yaml`)
- IDE配置 (`.vscode/`, `.idea/`)
- 个人简历材料 (`简历/`)

## 协作开发

### Fork工作流

1. Fork原仓库到你的账号
2. Clone你的fork
3. 添加上游仓库
4. 创建功能分支
5. 提交更改
6. 推送到你的fork
7. 创建Pull Request

```bash
# Clone你的fork
git clone https://github.com/your-username/pathomind.git

# 添加上游仓库
git remote add upstream https://github.com/original-owner/pathomind.git

# 同步上游更新
git fetch upstream
git checkout main
git merge upstream/main

# 创建功能分支
git checkout -b feature/my-feature

# 提交并推送
git add .
git commit -m "feat: my new feature"
git push origin feature/my-feature

# 在GitHub上创建Pull Request
```

## 获取帮助

- [Git官方文档](https://git-scm.com/doc)
- [GitHub文档](https://docs.github.com)
- [Pro Git书籍](https://git-scm.com/book/zh/v2)
