# 站点登录原理整理

## 1. 站点整体结构

这个站点是一个前后端分离的单页应用，首页只负责加载前端资源，真正的登录逻辑不在 HTML 表单里，而是在前端 JavaScript bundle 中通过 GraphQL 请求完成。

从前端 bundle 里可以确认几件事：

- 登录页路由是 `/user/login-form/login`
- 登录接口是 `POST /APIV2/GraphQL`
- 主要认证方式是 GraphQL 的 `Login` mutation
- 登录成功后返回 `token` 和 `user_info`
- 后续请求会把 `token` 放到 `Authorization` 头里

## 2. 登录流程

完整流程可以拆成以下几步：

### 2.1 获取验证码状态

先请求 `CaptchaData`。

这个接口会返回：

- `captcha_id`
- `captcha_base64_string`
- `need_verify`

含义如下：

- `need_verify = false` 时，通常可以不输入验证码，直接走登录
- `need_verify = true` 时，需要先把验证码图片展示出来或保存下来，人工输入验证码

### 2.2 提交登录 mutation

真正登录使用的是 GraphQL mutation `Login`，请求体里包含这些字段：

- `app_key`
- `account`
- `password`
- `captcha_id`
- `captcha_code`
- `google_code`
- `bank_card_real_name`
- `two_step_token`

其中最核心的是：

- `app_key`：前端固定的应用键
- `account`：账号
- `password`：密码
- `captcha_id` / `captcha_code`：验证码相关参数

### 2.3 登录成功后的返回值

登录成功后，接口会返回：

- `user_id`
- `token`
- `user_info`

其中 `token` 是后续会话最关键的内容。

### 2.4 会话维持

前端 GraphQL 客户端会从内部 token 提供器中读取 token，并把它写到 `Authorization` 请求头里。

这意味着：

- 登录成功后，只要拿到 token，就可以继续调用受保护接口
- 如果 token 失效，需要重新走登录流程

## 3. 抓包里容易混淆的两个请求

你前面抓到的两个包都不是最终登录包：

- `CaptchaData`：这是拿验证码状态和图片的前置包
- `UserGreeting`：这是账号问候信息查询，不产生登录态

真正登录的是 `Login` mutation。

## 4. Python 脚本实现思路

脚本实现建议如下：

1. 初始化 `requests.Session`
2. 先请求 `CaptchaData`
3. 如果 `need_verify = true`，保存验证码图片并等待人工输入
4. 调用 `Login` mutation
5. 从返回值提取 `token`
6. 将 `token` 写入本地文件，或者写到 session 头里
7. 使用同一个 session 调后续接口

### 4.1 推荐拆分为两个脚本（更清晰）

你提出的做法是正确的，推荐把“登录”和“下注”拆开：

1. `login.py`
	- 只负责登录
	- 成功后写入本地凭据文件
2. `bet.py`
	- 只负责下注
	- 启动时从本地凭据文件读取 token
	- 构造 `Authorization` 头发起下单请求

这样做的好处：

- 职责单一，代码更容易维护
- 登录失败和下注失败可以独立排查
- token 复用简单，避免每次下注都重新登录

### 4.2 本地文件建议

建议使用如下文件：

- `session_token.txt`：只保存 token 字符串
- `udid.txt`：保存设备标识
- `user_info.json`：保存登录返回用户信息（可选）

建议格式：

- `session_token.txt` 内容只保留一行 token，不加额外前缀
- 读取时使用 `strip()` 去掉换行

### 4.3 执行顺序

1. 先运行 `login.py`，更新 `session_token.txt`
2. 再运行 `bet.py`，读取 `session_token.txt` 发起下注
3. 如果下注返回 token 失效（如 401/鉴权错误），回到第 1 步重新登录

### 4.4 下注中的“期数”字段

下注请求里关键字段是 `game_cycle_id`，它就是当前期数。

- 每次下注都应使用“当前有效期数”
- `game_cycle_id` 过期会导致下单失败或被拒绝
- 建议在 `bet.py` 中将它作为必填参数传入

## 5. 当前脚本行为

当前脚本已经支持：

- 从命令行读取账号和密码
- 自动请求验证码状态
- 自动保存验证码图片（如果服务端返回图片）
- 提交 `Login` mutation
- 保存 `token`、`user_info` 和 `udid`

当 `need_verify = false` 时，脚本会直接在空验证码情况下登录，这正是当前站点的一种正常登录路径。

## 6. 常见失败原因

如果登录失败，通常是下面几类原因：

- 账号或密码错误
- `captcha_code` 不正确
- `app_key` 不匹配
- `udid` 与历史设备信息不一致
- token 失效后没有重新登录

## 7. 可复用结论

对于这个站点，自动登录不需要完整逆向整个前端项目，只需要掌握三件事：

- `CaptchaData` 的返回结构
- `Login` mutation 的参数结构
- `Authorization` 头使用的 token 形式

只要这三点对上，Python 就可以稳定复现登录。

另外在工程组织上，推荐采用“登录脚本 + 下注脚本”分离模式，并通过 `session_token.txt` 共享 token，这样更适合长期维护和自动化运行。
