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
    await bind.mainSetOption(
        key: 'custom-rendezvous-server', value: cfg['id_server']?.toString() ?? '');
    await bind.mainSetOption(
        key: 'relay-server', value: cfg['relay_server']?.toString() ?? '');
    await bind.mainSetOption(key: 'key', value: cfg['key']?.toString() ?? '');
    await bind.mainSetOption(
        key: 'api-server', value: cfg['api_server']?.toString() ?? '');
    await bind.mainSetLocalOption(key: kOptionTmsConfigApplied, value: 'Y');
  } catch (e) {
    debugPrint('applyTmsConfig failed: $e');
  }
}
