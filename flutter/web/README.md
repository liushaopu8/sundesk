# SunDesk Web

Web client build for SunDesk.

The web client reuses RustDesk's prebuilt WebAssembly modules (downloaded as
`web_deps.tar.gz` from the RustDesk releases) together with the JavaScript glue
in `flutter/web/js/` (built with `yarn build`) and the Flutter/Dart bridge in
`flutter/lib/web/`.

## Build

See the `build-rustdesk-web` job in `.github/workflows/flutter-build.yml`.
In short:

```
pushd flutter/web/js
yarn install && yarn build
popd

pushd flutter/web
wget https://github.com/rustdesk/doc.rustdesk.com/releases/download/console/web_deps.tar.gz
tar xzf web_deps.tar.gz
popd

flutter build web --release
```

This build is a preview and does not provide full functionality.
