# Git Workflow

## 推荐分支策略

- `main`: 稳定主分支，只保留已经完成并确认可用的版本
- `feature/<name>`: 功能开发分支，例如 `feature/login-page`
- `fix/<name>`: 问题修复分支，例如 `fix/email-report-time-window`

## 推荐开发流程

1. 先同步主分支

```bash
git checkout main
git pull --ff-only
```

2. 从 `main` 切出一个新分支

```bash
git checkout -b feature/your-change-name
```

3. 本地开发并提交

```bash
git status
git add .
git commit -m "feat: describe your change"
```

4. 推送到 GitHub

```bash
git push -u origin feature/your-change-name
```

5. 在 GitHub 上发起 PR，把这个分支合并回 `main`

6. PR 合并后，本地回到 `main` 并同步

```bash
git checkout main
git pull --ff-only
```

7. 删除已经完成的功能分支

```bash
git branch -d feature/your-change-name
```

如果远端分支也不需要了：

```bash
git push origin --delete feature/your-change-name
```

## 什么时候可以直接推 main

下面这些情况可以直接推 `main`：

- 只有你一个人维护项目
- 改动非常小，比如修文档或改几个字
- 你明确知道这次改动不需要单独评审

但长期来看，功能开发仍然建议走 `feature -> PR -> main`。

## 提交信息建议

- `feat: add daily git report`
- `fix: correct email time window`
- `docs: update github workflow`
- `refactor: simplify report generator`

## PR 是什么

PR 是 Pull Request，意思是“请求把我的分支改动合并到目标分支”。

在这个项目里，最常见的就是：

- 源分支：`feature/something`
- 目标分支：`main`

你可以把 PR 理解成 GitHub 上的一次“版本合并申请单”。
