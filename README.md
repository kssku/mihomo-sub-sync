# mihomo-sub-sync

Mihomo 订阅每日自动同步。

## 订阅直链

    https://raw.githubusercontent.com/kssku/mihomo-sub-sync/main/clash_proxies_latest.yaml

仓库是私密的，raw 直链公开访问会 404。本机读取用：

    curl -H "Authorization: token <你的token>" \
      https://raw.githubusercontent.com/kssku/mihomo-sub-sync/main/clash_proxies_latest.yaml

## 说明

- 每天北京时间 08:00 自动运行（UTC 00:00）
- 抓取失败或 YAML 校验不过时不会覆盖旧文件
- 历史归档在 archive/，保留 7 天
- 手动触发：Actions → Sync Mihomo Subscription → Run workflow
