# bet.py 使用说明

本文档说明如何使用 `bet.py` 完成自动下注，包括：

- 依赖前置文件
- 运行方式
- 参数解释
- 典型示例
- 常见问题排查

## 1. 脚本职责

`bet.py` 只负责下注，不负责登录。

它会：

1. 从本地文件读取 `token` 和 `udid`
2. 如果未手动指定期数，先查询当前 `cycle_id`
3. 发送 `AddLotteryOrders` 请求完成下注

## 2. 前置条件

在运行 `bet.py` 前，需要先跑 `login.py`，确保这些文件存在：

- `session_token.txt`：保存 token
- `udid.txt`：保存设备 ID
- `user_info.json`：可选；当不传 `--account` 时用于回退读取账号

## 3. 快速开始

### 3.1 推荐流程

1. 先登录（刷新 token）：

```bash
python login.py --account 你的账号 --password 你的密码
```

2. 再下注（自动查询当前期数）：

```bash
python bet.py
```

### 3.2 指定账号下注

```bash
python bet.py --account guajiyingli002
```

### 3.3 指定期数下注

```bash
python bet.py --account guajiyingli002 --game-cycle-id 59076660
```

## 4. 参数说明

### 4.1 账号与本地文件

- `--account`
  - 下注账号（用于请求参数 `ac`）
  - 可选
  - 不传时会从 `--user-info-file` 读取 `user_account`

- `--token-file`
  - token 文件路径
  - 默认：`session_token.txt`

- `--udid-file`
  - udid 文件路径
  - 默认：`udid.txt`

- `--user-info-file`
  - 回退读取账号的文件
  - 默认：`user_info.json`

### 4.2 玩法与期数

- `--game-id`
  - 游戏 ID
  - 默认：`370`

- `--game-type-id`
  - 玩法类型 ID
  - 默认：`65`

- `--game-cycle-id`
  - 期数 ID（当前期）
  - 不传时自动查询当前 `now_cycle_id`

- `--row-count`
  - 查询期数时历史记录数量
  - 默认：`30`

### 4.3 下注配置

- `--bet-info`
  - 核心选号结构（字符串）
  - 默认：`[[],["0","1","2","3","5","6","7","8","9"],[],[],[]]`

- `--bet-mode`
  - 下注模式
  - 默认：`OneLi`

- `--bet-multiple`
  - 倍数
  - 默认：`23`

- `--bet-percent-type`
  - 比例类型
  - 默认：`AdjustPercentType`

- `--bet-percent`
  - 比例值
  - 默认：`0`

- `--is-follow`
  - 是否跟单（布尔开关）
  - 默认：不跟单

- `--follow-commission-percent`
  - 跟单佣金比例
  - 默认：空

## 5. 自动查询期数逻辑

当未传 `--game-cycle-id` 时，脚本会调用 `GetLotteryCycle` 查询：

- 路径：`LotteryGame.lottery_cycle_now.now_cycle_id`
- 然后将该值作为 `game_cycle_id` 写入下单请求

也就是说，默认情况下会“先查当前期，再下单”。

## 6. 常用命令示例

### 6.1 完全默认下注（依赖本地文件）

```bash
python bet.py
```

### 6.2 指定倍数

```bash
python bet.py --bet-multiple 10
```

### 6.3 指定游戏和玩法

```bash
python bet.py --game-id 370 --game-type-id 65
```

### 6.4 指定期数并下单

```bash
python bet.py --game-cycle-id 59076660
```

## 7. 输出说明

成功时一般会输出两段：

1. 当前期信息（自动查期数时）
2. 下单结果，例如：

```json
{
  "message": "投注成功！",
  "order_ids": ["XXXXXX"],
  "__typename": "AddLotteryOrdersResult"
}
```

## 8. 常见问题

### 8.1 报错：token file not found

原因：`session_token.txt` 不存在。

处理：先运行 `login.py`，或通过 `--token-file` 指定正确路径。

### 8.2 报错：udid file not found

原因：`udid.txt` 不存在。

处理：先运行 `login.py`，或通过 `--udid-file` 指定正确路径。

### 8.3 报错：account not found in user_info.json

原因：未传 `--account`，且 `user_info.json` 缺少 `user_account`。

处理：

- 直接传 `--account`
- 或重新执行 `login.py` 更新 `user_info.json`

### 8.4 下单失败但脚本无语法错误

常见是业务侧原因：

- token 过期
- 期数过期
- 余额不足
- 风控限制

建议：

1. 重新运行 `login.py` 刷新 token
2. 不手动传 `--game-cycle-id`，让脚本自动取当前期
3. 检查 `bet-info` 与玩法是否匹配

## 9. 安全建议

- 不要把 `session_token.txt` 提交到代码仓库
- token 视同登录凭据，泄露后应立即重新登录
- 定期刷新 token，避免长时间使用旧凭据
