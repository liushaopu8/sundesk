import 'dart:convert';
import 'dart:io';

import 'package:flutter/foundation.dart';

import '../common.dart';
import '../consts.dart';
import 'platform_model.dart';

/// Apply the ID/Relay server config pushed down by TMS.
///
/// Reads [kTmsConfigPath] and writes the values into the Rust core options.
/// Once applied, the in-app "ID/Relay Server" entry is hidden (see
/// [kOptionTmsConfigApplied]) so the user cannot change the server manually.
Future<void> applyTmsConfig() async {
  if (!isAndroid) return;
  final file = File(kTmsConfigPath);
  if (!await file.exists()) {
    return;
  }
  try {
    final cfg = jsonDecode(await file.readAsString());
    if (cfg is! Map<String, dynamic>) {
      debugPrint('applyTmsConfig: unexpected json type: ${cfg.runtimeType}');
      return;
    }
    // 必须三字段：id_server、relay_server、key 都非空，才算合法 TMS 配置
    final idServer = cfg['id_server']?.toString() ?? '';
    final relayServer = cfg['relay_server']?.toString() ?? '';
    final key = cfg['key']?.toString() ?? '';
    if (idServer.isEmpty || relayServer.isEmpty || key.isEmpty) {
      debugPrint('applyTmsConfig: missing required fields, ignoring config');
      return;
    }
    await bind.mainSetOption(key: 'custom-rendezvous-server', value: idServer);
    await bind.mainSetOption(key: 'relay-server', value: relayServer);
    await bind.mainSetOption(key: 'key', value: key);
    // api_server 可选：有就写，没有就保留原值
    final apiServer = cfg['api_server']?.toString() ?? '';
    if (apiServer.isNotEmpty) {
      await bind.mainSetOption(key: 'api-server', value: apiServer);
    }
    final unattendedPwd = cfg['unattended_password']?.toString() ?? '';
    final settingsSecret = cfg['settings_secret']?.toString() ?? '';
    if (unattendedPwd.isNotEmpty) {
      await bind.mainSetLocalOption(
          key: kOptionTmsUnattendedPassword, value: unattendedPwd);
      // 立即把连接密码写进 Rust core，无需等用户去拨无人值守开关。
      await bind.mainSetPermanentPasswordWithResult(password: unattendedPwd);
    }
    if (settingsSecret.isNotEmpty) {
      await bind.mainSetLocalOption(
          key: kOptionTmsSettingsSecret, value: settingsSecret);
    }
    // 仅当必填字段齐全时才标记已应用，隐藏设置入口
    await bind.mainSetLocalOption(key: kOptionTmsConfigApplied, value: 'Y');
  } catch (e) {
    debugPrint('applyTmsConfig failed: $e');
  }
}
