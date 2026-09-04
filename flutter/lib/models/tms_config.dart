import 'dart:convert';
import 'dart:io';

import 'package:flutter/foundation.dart';

import '../common.dart';
import '../consts.dart';
import 'platform_model.dart';

/// Apply the ID/Relay server config pushed down by TMS.
///
/// Reads [kTmsConfigPath] and writes the values into the Rust core options.
/// Server fields (rendezvous-server/relay-server/key) are required; api-server is optional.
/// TMS config is re-applied on every startup; manual overrides in Settings are preserved
/// (settings are protected by settings-secret).
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
    // Required fields from TMS (kebab-case keys).
    final idServer = cfg['rendezvous-server']?.toString() ?? '';
    final relayServer = cfg['relay-server']?.toString() ?? '';
    final key = cfg['key']?.toString() ?? '';
    if (idServer.isEmpty || relayServer.isEmpty || key.isEmpty) {
      debugPrint('applyTmsConfig: missing required fields, ignoring config');
      return;
    }
    await bind.mainSetOption(key: 'custom-rendezvous-server', value: idServer);
    await bind.mainSetOption(key: 'relay-server', value: relayServer);
    await bind.mainSetOption(key: 'key', value: key);
    // api-server (optional).
    final apiServer = cfg['api-server']?.toString() ?? '';
    if (apiServer.isNotEmpty) {
      await bind.mainSetOption(key: 'api-server', value: apiServer);
    }
    // access-password → unattended access password.
    final accessPwd = cfg['access-password']?.toString() ?? '';
    if (accessPwd.isNotEmpty) {
      await bind.mainSetLocalOption(
          key: kOptionTmsUnattendedPassword, value: accessPwd);
      await bind.mainSetPermanentPasswordWithResult(password: accessPwd);
      await bind.mainSetOption(key: 'enable-unattended-access', value: 'Y');
    }
    // settings-secret → settings secret.
    final settingsSecret = cfg['settings-secret']?.toString() ?? '';
    if (settingsSecret.isNotEmpty) {
      await bind.mainSetLocalOption(
          key: kOptionTmsSettingsSecret, value: settingsSecret);
      await bind.mainSetOption(key: 'settings-secret', value: settingsSecret);
    }
    debugPrint('applyTmsConfig: host = ${idServer}');
  } catch (e) {
    debugPrint('applyTmsConfig failed: $e');
  }
}
