# bet 参数可能取值记录

本文档用于记录 `bet.py` / `AddLotteryOrders` 相关参数的可能取值。

标记说明：

- 已验证：抓包或实测成功出现过
- 结构已知：字段类型和作用明确，但枚举集合未完全确认
- 待试验：建议纳入测试矩阵

## 1. 请求级参数（URL / Header）

### 1.1 URL Query 参数

- `l`
  - 类型：string
  - 已验证：`zh-cn`

- `pf`
  - 类型：string
  - 已验证：`web`

- `udid`
  - 类型：string
  - 已验证：UUID 风格字符串，例如 `b9bb9c21-f51d-45bd-85e5-27d99c8a2b42`

- `ac`
  - 类型：string
  - 含义：账号
  - 已验证：`guajiyingli002`

### 1.2 Header 参数

- `authorization`
  - 类型：string
  - 含义：登录 token
  - 说明：必须有效；过期后需要重新登录刷新

## 2. 查询当前期数参数（GetLotteryCycle）

### 2.1 入参

- `game_id`
  - 类型：int
  - 已验证：`370`

- `row_count`
  - 类型：int
  - 已验证：`30`
  - 说明：影响历史开奖返回条数，不影响当前期数主逻辑

### 2.2 关键出参

- `LotteryGame.lottery_cycle_now.now_cycle_id`
  - 类型：int
  - 含义：当前期数 ID（下注使用）

- `LotteryGame.lottery_cycle_now.now_cycle_value`
  - 类型：string
  - 含义：当前期号显示值

## 3. 下单参数（AddLotteryOrders.variables.input[0]）

### 3.1 基础字段

- `game_id`
  - 类型：int
  - 已验证：`370`
  - 含义：彩种类型（如 370 代表某彩种）

- `game_type_id`
  - 类型：int
  - 已验证：`65`
  - 含义：玩法类型（如 65 代表该彩种下的某个玩法）
  - 说明：存在其他可用值，待试验

- `game_cycle_id`
  - 类型：int
  - 说明：应使用当前有效期（建议由 GetLotteryCycle 自动获取）

### 3.2 下注结构与模式

- `bet_info`
  - 类型：string（内部是 JSON 结构串）
  - 已验证：
    - `[[],["0","1","2","3","5","6","7","8","9"],[],[],[]]`
    - `[[],["0","1","2","3","4","5","6","7","8"],[],[],[]]`
  - 结构规则：
    - 固定为 5 个位置（即 5 个子数组）
    - 每个位置可选数字范围为 `0-9`
    - 每个位置最多选择 9 个数字
  - 说明：核心投注内容，通常与 `game_type_id` 强相关

- `bet_mode`
  - 类型：string（枚举）
  - 已验证（八档已全量验证）：`TwoYuan`、`TwoJiao`、`TwoFen`、`TwoLi`、`OneYuan`、`OneJiao`、`OneFen`、`OneLi`
  - 八档金额模式（已整理）：
    - `TwoYuan` -> 2元
    - `TwoJiao` -> 2角
    - `TwoFen` -> 2分
    - `TwoLi` -> 2厘
    - `OneYuan` -> 1元
    - `OneJiao` -> 1角
    - `OneFen` -> 1分
    - `OneLi` -> 1厘
  - 说明：命名规则为 `One/Two + Yuan/Jiao/Fen/Li`

### 3.3 数值参数

- `bet_multiple`
  - 类型：int
  - 已验证：`1`、`23`、`100`
  - 待试验：`2, 5, 10, 20, 50`

- `bet_percent_type`
  - 类型：string（枚举）
  - 已验证：`AdjustPercentType`
  - 待试验：其他百分比分配类型

- `bet_percent`
  - 类型：int
  - 已验证：`0`
  - 待试验：`1, 5, 10, 20, 50, 100`（是否允许由后端规则决定）

### 3.4 跟单相关

- `is_follow`
  - 类型：bool
  - 已验证：`false`
  - 待试验：`true`

- `follow_commission_percent`
  - 类型：number 或 null
  - 已验证：`null`
  - 待试验：`0, 1, 5, 10`（仅在 `is_follow=true` 时测试）

## 4. 已验证可用组合

组合 A（成功）：

- `game_id=370`
- `game_type_id=65`
- `game_cycle_id=自动查询 now_cycle_id`
- `bet_info=[[],["0","1","2","3","5","6","7","8","9"],[],[],[]]`
- `bet_mode=OneLi`
- `bet_multiple=23`
- `bet_percent_type=AdjustPercentType`
- `bet_percent=0`
- `is_follow=false`
- `follow_commission_percent=null`

组合 B（成功）：

- `game_id=370`
- `game_type_id=65`
- `game_cycle_id=59076690/59076691`（抓包样例）
- `bet_info=[[],["0","1","2","3","4","5","6","7","8"],[],[],[]]`
- `bet_mode=OneFen/TwoLi/TwoFen/TwoJiao`
- `bet_multiple=100`
- `bet_percent_type=AdjustPercentType`
- `bet_percent=0`
- `is_follow=false`
- `follow_commission_percent=null`

## 5. 建议测试矩阵（逐项单变量）

建议一次只改一个参数，其他保持“组合 A”不变：

1. `bet_multiple`: `2 -> 5 -> 10 -> 20 -> 50`
2. `bet_percent`: `0 -> 1 -> 5 -> 10`
3. `is_follow`: `false -> true`
4. `follow_commission_percent`: 在 `is_follow=true` 下从 `0 -> 1 -> 5`
5. `game_type_id`: 收集候选值后逐个测试
6. `bet_info`: 继续收集不同玩法结构样例

每次记录：

- 请求参数快照
- 返回 `message`
- 是否成功
- `order_ids` 是否返回
- 失败错误文本

## 6. 与 bet.py 参数映射

- `--game-id` -> `game_id`
- `--game-type-id` -> `game_type_id`
- `--game-cycle-id` -> `game_cycle_id`
- `--bet-info` -> `bet_info`
- `--bet-mode` -> `bet_mode`
- `--bet-multiple` -> `bet_multiple`
- `--bet-percent-type` -> `bet_percent_type`
- `--bet-percent` -> `bet_percent`
- `--is-follow` -> `is_follow=true`
- `--follow-commission-percent` -> `follow_commission_percent`

## 7. 维护建议

- 每次抓到新请求，先更新本文件“已验证”区。
- 未确认的候选值统一放“待试验”，避免混淆。
- 如果后端规则变化（例如风控或最小倍数），单独加版本记录。