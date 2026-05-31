# Log Monitoring Tool

远程实时日志监控工具，通过 SSH 连接 Linux 服务器，自动切换 root 权限，实时流式输出日志内容并支持日志级别高亮和过滤。

## 功能特性

- SSH 远程连接 Linux 服务器
- 自动 root 切换（优先 `su`，失败自动回退 `sudo su`）
- 实时日志流式输出（类似 `tail -f`）
- 日志级别颜色高亮（ERROR 红 / WARN 黄 / INFO 绿 / DEBUG 灰）
- 支持多环境配置管理（JSON 存储）
- CLI 和 GUI 两种使用方式

## 安装

```bash
pip install -r requirements.txt
```

依赖：paramiko、python-dotenv、pyside6

## 使用

### CLI 版本

1. 编辑 `.env` 文件配置服务器信息：

```
HOST=192.168.31.11
PORT=22
USERNAME=lan
PASSWORD=your_password

ROOT_USER=
ROOT_PASS=

LOG_PATH=/var/log/syslog
```

2. 运行：

```bash
python main.py
```

### GUI 版本

```bash
python main_gui.py
```

1. 点击菜单栏「环境配置」→「管理环境」添加服务器
2. 在下拉菜单选择环境，点击「连接」
3. 中间区域显示全量日志，底部左侧勾选过滤级别，右侧显示过滤结果

## 项目结构

```
log_monitoring/
├── main.py               # CLI 入口
├── main_gui.py           # GUI 入口
├── core/
│   ├── ssh_client.py     # SSH 连接与 root 切换
│   ├── env_manager.py    # 环境配置管理（JSON）
│   └── log_viewer.py     # 日志级别检测
├── gui/
│   ├── main_window.py    # 主窗口布局
│   ├── env_dialog.py     # 环境管理弹窗
│   ├── log_widget.py     # 日志显示组件
│   ├── filter_widget.py  # 日志级别过滤
│   └── ssh_worker.py     # SSH 异步工作线程
├── .env                  # CLI 配置文件
└── environments.json     # GUI 环境配置
```

## 配置说明

| 字段 | 说明 |
|------|------|
| HOST | 服务器地址 |
| PORT | SSH 端口，默认 22 |
| USERNAME | SSH 用户名 |
| PASSWORD | SSH 密码 |
| ROOT_USER | root 用户名（可选） |
| ROOT_PASS | root 密码（可选，为空则用当前用户密码通过 sudo 切换） |
| LOG_PATH | 要监控的日志文件路径 |

## Root 切换策略

工具会自动尝试两种方式获取 root 权限：

1. **`su -`**：使用 ROOT_PASS 作为密码
2. **`sudo su -`**：使用当前用户密码（当 su 失败或 ROOT_PASS 为空时）

无需手动配置，工具会自动检测并切换。
