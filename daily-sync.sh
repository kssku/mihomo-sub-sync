#!/bin/bash
# Mihomo 订阅每日同步：本机抓取 -> git push
set -u
cd /root/GitHub/mihomo-sub-sync || exit 1
LOG=/tmp/mihomo-sub-sync.log
echo "===== $(date +%F_%T) =====" >> "$LOG"

/usr/bin/python3 sync_mihomo.py >> "$LOG" 2>&1
RC=$?
if [ "$RC" -ne 0 ]; then
  echo "fetch failed rc=$RC, abort" >> "$LOG"
  exit "$RC"
fi

if git diff --quiet -- clash_proxies_latest.yaml; then
  echo "no change" >> "$LOG"
  exit 0
fi

git add clash_proxies_latest.yaml archive
git -c user.name="kssku" -c user.email="162272168+kssku@users.noreply.github.com" commit -m "chore: sync subscription" >> "$LOG" 2>&1
GIT_SSH_COMMAND="ssh -i /root/.ssh/id_ed25519_github -o StrictHostKeyChecking=no" git push >> "$LOG" 2>&1
echo "push rc=$?" >> "$LOG"