# SunDesk Android — 项目记忆

> 最后更新：2026-08-28

## ⚠️ 部署状态（2026-08-28 甫总拍板）

**当前装机 APK 不含 uuid 解耦**，处于「中间状态」：
- ✅ 已在包里：id=SN、pk=SHA256(SN) 确定性派生（约 commit 45e1b5e 状态）
- ❌ 不在包里：uuid 解耦（主仓 `871217d` + hbb_common `55ba5d7`，仅在 `log/sn-seed-trace` 分支）
- 实测：logcat 无 `[sundesk-uuid] uuid from SN seed`；register_pk 的 uuid 是 **32 字节**且与 pk 逐字节相同；hbbs `update_pk` 行两数组一致
- **为什么不咬人**：pk 确定性 + DB 旧行已清 → 重装 pk 不变，hbbs 永远认老设备。uuid=pk 只在需要轮换 pk 时才会变成问题（服务器规则：uuid 相同才允许换 pk）
- **决策**：保持现状，等 log/sn-seed-trace 合并/出正式包时顺带带上解耦
- **将来上解耦包必做**：装前 `DELETE FROM peers WHERE id='S200XE22614E0010';`（uuid 32B→16B 首登会 mismatch 一次）；验证标志：`[sundesk-uuid] uuid from SN seed` 为 16 字节、update_pk 两数组长度不同
- 注意：修复只在 `log/sn-seed-trace`，远程 main / sundesk-android 分支都没有；CI 仅 push main 自动构建，手动构建需 workflow_dispatch 选该分支

---

## 项目目标

将 RustDesk 1.2.5 定制为 SunDesk Android 客户端，核心改动：
- **id 固定为硬件 SN**（`S200XE22614E0010`），不依赖随机 ID
- **密钥对由 SN 确定性派生**，重装不丢
- **uuid 独立于 pk**，修复移动端注册死循环

---

## 核心身份模型（三者的关系）

```
        id              uuid              pk
      （名字）         （指纹）         （钥匙）
     ┌──────────┐    ┌──────────┐    ┌──────────────┐
     │ 硬件 SN  │    │ SHA256(SN)│    │ ed25519 公钥  │
     │ 给人拨号  │    │ 前16字节  │    │ 端到端加密根  │
     │ 永不换   │    │ 永不换   │    │ SN 派生，可轮换│
     └──────────┘    └──────────┘    └──────────────┘
         │               │                 │
         └───── 注册时一起发给 hbbs ────────┘
                     hbbs 存：id → (uuid, pk)
```

| 字段 | 用途 | 来源 | 稳定性 |
|------|------|------|--------|
| **id** | 拨号地址（控制端输入的号码） | 硬件 SN | 永不换 |
| **uuid** | hbbs 认设备的指纹（不参与加密） | SHA256(SN)[..16] | 永不换 |
| **pk** | ed25519 公钥，控制端↔被控端加密 | SHA256(SN) → keypair_from_seed | 可轮换（重装不变） |

### 注册流程

```
客户端 → hbbs:  {id, uuid, pk}

hbbs 判断逻辑：
├─ id 没记录 → 全新注册，登记 OK
├─ id 有记录，uuid 相同 → 同一设备换 pk，更新 OK
├─ id 有记录，uuid 不同 → 冒充 → UUID_MISMATCH 拒绝
└─ 短时间注册太多次 → TOO_FREQUENT 限流
```

---

## 关键改动清单

### 1. 硬件 SN 身份

- **文件**：`src/flutter_ffi.rs`（JNI `startServer`）
- **改动**：从 `SystemProperties.serialno` 读取 SN，调 `Config::set_id(&sn)` 覆盖随机 id
- **日志标签**：`[sundesk-seed]`

### 2. 确定性密钥对

- **文件**：`libs/hbb_common/src/config.rs`（`set_key_pair_from_seed`）
- **改动**：SHA256(SN) 做 ed25519 seed，`keypair_from_seed` 派生
- **效果**：卸载重装后 pk 和 sk 和之前完全一样，hbbs 不会 mismatch

### 3. uuid 独立于 pk（修复 UUID_MISMATCH 死循环）

- **根因**：上游 RustDesk 移动端 `get_uuid()` 即返回 `Config::get_key_pair().1`（pk），因为官方移动端 id 是随机的，重装全换不冲突。但我们把 id 钉死成 SN，uuid 却还跟着会变的 pk 走，导致 hbbs 永远判 UUID_MISMATCH。
- **修复**：
  - `libs/hbb_common/src/config.rs`：Config 结构体加 `uuid: Vec<u8>` 字段 + `UUID_CACHE`；新增 `get_persistent_uuid()` / `set_uuid_from_seed()`（SHA256(SN) 前16字节）
  - `libs/hbb_common/src/lib.rs`：`get_uuid()` 在 android/ios 分支改调 `get_persistent_uuid()`（桌面走 machine_uid 不变）
  - `src/flutter_ffi.rs`：JNI 里 set_key_pair_from_seed 后紧跟 set_uuid_from_seed(SN)
- **日志标签**：`[sundesk-uuid]`

### 4. UUID_MISMATCH 时轮换 pk

- **文件**：`src/rendezvous_mediator.rs`（`handle_uuid_mismatch`）
- **改动**：对 SN ID 不再复用旧 pk，调 `Config::update_key_pair()` 生成随机新 pk
- **日志标签**：`[sundesk-seed] update_key_pair`

---

## 提交历史

| 日期 | 提交 | 说明 |
|------|------|------|
| 2026-08-27 | hbb_common `55ba5d7` | uuid 与 pk 解耦，SN 派生 uuid |
| 2026-08-27 | 主仓库 `871217d` | JNI 播种 uuid，submodule bump |
| 2026-08-27 | hbb_common `4c0d663` | 新增 `update_key_pair()` |
| 2026-08-27 | 主仓库 `cf3e2f3` | UUID_MISMATCH 时换 keypair |
| 2026-08-26 | 主仓库 `e810bd2` | 修复 E0004 编译错误（non_exhaustive match） |

---

## 服务器信息

- **hbbs/hbbr**：`172.16.1.238`（内网）
- **端口**：21116 UDP（hbbs）、21114 HTTP（api）、21115 TCP（NAT 穿透）
- **测试设备 SN**：`S200XE22614E0010`
- **注意**：旧记录 uuid=pk，必须删除后重新注册

---

## 常见问题

### Q: 为什么 uuid 和 pk 之前一样？
A: 上游 RustDesk 移动端 `get_uuid()` 末尾直接返回 `Config::get_key_pair().1`（pk），因为官方设计里移动端 id 每次重装都是随机的，uuid 和 pk 一起换没问题。我们的定制把 id 固定成了 SN，但 uuid 还跟着 pk 走，导致重装后 id 不变、uuid 变了，hbbs 判定为冒充。

### Q: 重装后会不会又被 UUID_MISMATCH？
A: 目标状态（log/sn-seed-trace）：不会，id、pk、uuid 全部从 SN 确定性派生，重装后三个值完全一样。
**当前装机包（2026-08-28 状态）**：uuid 还等于 pk（32B），但 pk 已确定性派生，重装后 pk/uuid 仍和之前一样，所以实测也不会 mismatch。

### Q: 如果服务器端 key_confirmed 过期了怎么办？
A: 目标状态：`handle_uuid_mismatch` 会调 `update_key_pair()` 生成随机新 pk，同时 uuid 不变，hbbs 认 uuid 相同接受更新。但这种方式会失去确定性 pk 的好处（控制端存旧的 pk 会握手失败，需重新查询）。
**当前装机包没有 uuid 解耦，此路不通**——随机换 pk 会连带换 uuid，必然 UUID_MISMATCH。这也是解耦修复待合并的主要理由。

---

## 未来待办

- [ ] 竞态处理：Flutter `main_get_my_id()` 在 JNI SN 播种前可能生成随机 id，观察是否需加锁
- [ ] 服务器端旧记录删除后，确认全新注册流程走通
- [ ] 考虑 CI 自动触发 workflow