# TMP

## 项目说明

这个仓库用于整理 `ews.mtyl0.com` 的登录和下注流程，并把相关参数拆分成可复用的脚本：

- `login.py`：负责登录并保存 `session_token.txt`、`udid.txt`、`user_info.json`
- `gen_bet_params.py`：交互式生成下注参数 JSON 文件 `bet_params.json`
- `bet.py`：默认读取 `bet_params.json`，自动查询当前期数后提交下注

## 文件流转

典型流程如下：

1. 先运行 `login.py`，更新登录态文件
2. 再运行 `gen_bet_params.py` 生成下注参数文件
3. 最后运行 `bet.py`，它会从 JSON 文件读取参数并执行下单

相关文件：

- `session_token.txt`：登录 token
- `udid.txt`：设备标识
- `user_info.json`：登录返回的用户信息
- `bet_params.json`：下注参数文件

## 脚本使用

### 登录

```bash
python login.py --account 你的账号 --password 你的密码
```

### 生成下注参数

```bash
python gen_bet_params.py
```

### 执行下注

```bash
python bet.py
```

默认情况下，`bet.py` 会：

- 从 `bet_params.json` 读取下注参数
- 从 `session_token.txt` 读取 token
- 从 `udid.txt` 读取 udid
- 自动查询当前期数 `game_cycle_id`

如需临时覆盖 JSON 里的参数，也可以在命令行显式传参。

## 参数说明

下注参数的详细取值记录见 [bet_param_values.md](bet_param_values.md)。

## 说明

- `game_id` 表示彩种类型
- `game_type_id` 表示玩法类型
- `game_cycle_id` 表示当前期数
- `bet_info` 是 5 个位置的选号结构
- `bet_mode` 表示单注金额档位

如果后续新增更多玩法或彩种，可以继续在 `bet_param_values.md` 中补充对应记录。