# Uni-Aurapose

ProfitAI 项目仓库，包含前端页面、Python 后端、数据库初始化脚本，以及基于 `git log` 的日报邮件脚本。

## 项目结构

- `pages/`: UniApp 页面
- `python_backend/`: Python 服务与模型文件
- `mysql/init/`: MySQL 初始化脚本
- `automation/daily_change_report.py`: 基于 Git 提交记录生成日报并发送邮件
- `automation/daily_change_report.env.example`: 邮件配置模板

## GitHub 使用方式

### 首次拉取

```bash
git clone https://github.com/LesleyClancy/Uni-Aurapose.git
cd Uni-Aurapose
git lfs install
git lfs pull
```

### 日常提交流程

```bash
git status
git add .
git commit -m "feat: describe your change"
git push origin main
```

### 查看最近提交

```bash
git log --oneline --decorate -10
```

## 邮件日报

1. 复制 `automation/daily_change_report.env.example` 为 `automation/daily_change_report.env`
2. 填入 QQ 发件邮箱和 SMTP 授权码
3. 运行下面命令测试

```bash
python automation/daily_change_report.py --root .
```

脚本默认统计最近一个完整的“上午 10 点到次日上午 10 点”窗口，并将这段时间内的 Git 提交整理成邮件发送。
