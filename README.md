# mihomo-sub-sync

Mihomo 订阅每日自动同步。**抓取在本地机器执行**（住宅 IP），推送到本仓库分发。

## 订阅直链

    https://raw.githubusercontent.com/kssku/mihomo-sub-sync/main/clash_proxies_latest.yaml

备用镜像（jsDelivr，国内通常更快）：

    https://cdn.jsdelivr.net/gh/kssku/mihomo-sub-sync@main/clash_proxies_latest.yaml

> 本仓库为**公开仓库**，raw 直链无需鉴权。
> 国内直连 raw 可能被重置，客户端请走代理，或使用上面的 jsDelivr 镜像。

## 工作方式

    本地 cron (每天 04:17)
      └─ sync_mihomo.py 抓订阅 → 校验 YAML
           └─ git push → 本仓库
                └─ mihomo 客户端拉取 raw 链接

## 为什么不放 GitHub Actions

机场对机房 IP（GitHub Actions、Cloudflare Worker）返回空节点列表，直连 / WARP / 借道代理均已实测失败。
只有住宅 IP 能拿到完整节点，因此抓取必须在本机执行。

## 手动同步

    cd /root/GitHub/mihomo-sub-sync
    python3 sync_mihomo.py
    git add clash_proxies_latest.yaml archive
    git commit -m "chore: sync subscription"
    git push

## 说明

- 抓取失败或 YAML 校验不通过时**不覆盖**旧文件
- 历史归档在 archive/，保留 7 天
- 脚本使用浏览器 UA（机场对 clash / mihomo UA 返回 429）
