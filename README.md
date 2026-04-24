# Uni-Aurapose

ProfitAI 项目仓库，包含 UniApp 前端、Python 后端、MySQL 初始化脚本，以及基于 `git log` 的日报邮件脚本。

## 项目结构

- `pages/`: UniApp 页面
- `python_backend/`: Python 服务和模型文件
- `mysql/init/`: MySQL 初始化脚本
- `automation/daily_change_report.py`: 基于 Git 提交记录生成日报并发送邮件
- `automation/daily_change_report.env.example`: 邮件配置模板
- `CONTRIBUTING.md`: 分支开发和协作流程说明

## 首次拉取

```bash
git clone https://github.com/LesleyClancy/Uni-Aurapose.git
cd Uni-Aurapose
git lfs install
git lfs pull
```

## 日常开发

推荐使用 `main + feature` 分支模式：

- `main`: 保持稳定，随时可以作为当前正式版本
- `feature/*`: 开发具体功能或修复具体问题

一个完整开发流程如下：

```bash
git pull --ff-only
git checkout main
git checkout -b feature/home-page-refresh
```

开发完成后提交：

```bash
git status
git add .
git commit -m "feat: refresh home page"
git push -u origin feature/home-page-refresh
```

如果你暂时一个人开发，也可以先直接推到 `main`，但更推荐先推 `feature` 分支，再合并回 `main`。

## 什么是 PR

PR 是 Pull Request，可以理解成“合并申请”。

它的作用是：

- 把 `feature` 分支里的改动，申请合并到 `main`
- 在合并前先看清楚改了什么
- 方便以后自己回看每次版本是为什么改的
- 如果以后多人协作，别人也能先 review 再合并

你现在一个人开发，也依然建议用 PR，因为它天然就是“版本记录 + 合并记录”。

## 查看历史版本

```bash
git log --oneline --decorate -10
```

查看某次提交的具体改动：

```bash
git show 提交号
```

比如：

```bash
git show 6cc4f8b
```

## 按版本存储

可以。

最基础的“版本存储”就是 Git 提交历史。你每次执行一次 `git commit`，仓库里就多了一个可回退、可查看、可比较的版本。

如果你想要更正式的版本号，比如 `v0.1.0`、`v0.2.0`，可以在某次稳定提交上打标签：

```bash
git tag v0.1.0
git push origin v0.1.0
```

查看所有标签：

```bash
git tag
```

## 邮件日报

1. 复制 `automation/daily_change_report.env.example` 为 `automation/daily_change_report.env`
2. 填入 QQ 发件邮箱和 SMTP 授权码
3. 运行下面命令测试

```bash
python automation/daily_change_report.py --root .
```

脚本默认统计最近一个完整的“上午 10 点到次日上午 10 点”窗口，并将这段时间内的 Git 提交整理成邮件发送。

## 推荐习惯

- 每完成一个小功能就提交一次，不要攒很久再一起提交
- 提交信息尽量写清楚，例如 `feat:`、`fix:`、`docs:`
- 推送前先 `git pull --ff-only`
- 大改动优先新建 `feature` 分支
- 合并完成后可以删除已经用完的 `feature` 分支
