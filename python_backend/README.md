# ProFitAI Python Backend

这个后端现在同时负责两类能力：

- 实时动作识别：调用现有模型、返回动作/次数/关键点。
- 小程序业务数据：用户档案、首页概览、课程、训练模块、训练会话、训练记录、成就。

所有新增配置、SQL、MySQL 数据目录约定都在项目目录内，没有放到 C 盘或其他目录。

## 目录

- `server.py`：Flask API 服务。
- `db.py`：MySQL 连接与查询封装。
- `.env`：本地数据库连接配置。
- `requirements.txt`：Python 依赖。
- `../mysql/init/001_schema.sql`：建表脚本。
- `../mysql/init/002_seed.sql`：初始模板数据。
- `../mysql/data/`：本地 MySQL 数据目录，配合 `docker-compose.mysql.yml` 使用。

## 启动 MySQL

在项目根目录执行：

```bash
docker compose -f docker-compose.mysql.yml up -d
```

这会把 MySQL 数据放在：

```text
D:\uni-ProfitAI\ProfitAI\mysql\data
```

如果你使用本机已安装的 MySQL，也可以手动执行：

```bash
mysql -uroot -p < mysql/init/001_schema.sql
mysql -uroot -p < mysql/init/002_seed.sql
```

然后修改 `python_backend/.env` 里的账号密码。

## 启动后端

在 `python_backend` 目录执行：

```bash
pip install -r requirements.txt
python server.py
```

健康检查：

```text
GET http://127.0.0.1:5000/api/health
```

真机调试时，小程序不能访问电脑自己的 `127.0.0.1`，要把 `common/api.js` 里的 `API_BASE_URL` 改成电脑的局域网 IP，例如：

```js
export const API_BASE_URL = 'http://192.168.31.120:5000'
```

## 主要接口

- `GET /api/health`
- `GET /api/app/bootstrap?openid=dev-openid`
- `POST /api/auth/wechat-login`
- `POST /api/users/upsert`
- `GET /api/users/<openid>/profile`
- `GET /api/courses`
- `GET /api/challenges`
- `GET /api/training/modules`
- `POST /api/training/sessions`
- `POST /api/training/sessions/<session_id>/finish`
- `GET /api/users/<openid>/sessions`
- `POST /api/detect`
- `POST /api/realtime_frame`
- `POST /api/reset`

`/api/realtime_frame` 和 `/api/detect` 如果收到 `session_id`，会自动把识别结果写入 `training_records`，并汇总到 `training_sessions`。
