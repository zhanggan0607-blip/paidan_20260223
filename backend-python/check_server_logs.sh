#!/bin/bash
ssh -o StrictHostKeyChecking=no root@8.153.93.123 "podman logs sstcp-backend-new --tail 500 2>&1 | grep -E 'WX-LJ-2025-084A-SH|photos|PATCH|upload'"
