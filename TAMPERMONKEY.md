# Tampermonkey 用法

这个项目现在额外提供了油猴脚本版：[uestc_xtzx_helper.user.js](/home/saverm/XueTang/2026_UESTC_XTZX_HELPER/uestc_xtzx_helper.user.js)。

## 适用场景

- 你已经登录学堂在线
- 想直接在课程视频页面操作
- 不想再手动改 `config.py`

## 怎么用

1. 安装 Tampermonkey。
2. 新建脚本，把 [uestc_xtzx_helper.user.js](/home/saverm/XueTang/2026_UESTC_XTZX_HELPER/uestc_xtzx_helper.user.js) 的内容粘进去保存。
3. 打开学堂在线某个视频页面。
4. 按 `F12` 打开开发者工具，在网络里找到 `heartbeat` 请求。
5. 右键该请求，复制为 `curl(bash)`。
6. 回到页面右下角浮窗，把 curl 粘进去，点“保存 heartbeat 模板”。
7. 直接点“刷当前视频”，或者填起止视频 ID 后点“刷起止区间”。

## 说明

- `sign`、`cid`、当前视频 ID 会直接从当前页面 URL 读取。
- `u`、`c`、`skuid`、`cc`、默认 `d` 会从你粘贴的 heartbeat curl 中读取。
- 浏览器已经登录的前提下，`cookies` 会自动跟随当前页面请求发送。
- 这里的“视频 ID”沿用原 Python 脚本逻辑，按数值区间递增提交。

## 限制

- 目前还是基于你手动从 F12 拿到一次 heartbeat 模板，不是全自动抓包。
- 如果课程视频 ID 不是连续的，区间模式可能会跳到不存在的视频 ID。
- 请求过快仍然可能被限速，建议适当调大浮窗里的间隔毫秒。
