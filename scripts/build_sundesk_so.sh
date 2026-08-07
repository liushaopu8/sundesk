#!/bin/bash
set -e
export PATH=/root/.cargo/bin:$PATH
export ANDROID_NDK_HOME=/opt/android-ndk-r27c
export ANDROID_NDK=/opt/android-ndk-r27c
export VCPKG_ROOT=/opt/vcpkg
cd /mnt/d/support/system/sundesk-master

echo "===== [0] vcpkg bootstrap (if needed) ====="
if [ ! -f /opt/vcpkg/vcpkg ]; then
  cd /opt/vcpkg
  VCPKG_FORCE_SYSTEM_BINARIES=1 ./bootstrap-vcpkg.sh 2>&1 | tail -5
  cd /mnt/d/support/system/sundesk-master
fi
/opt/vcpkg/vcpkg version

echo "===== [1] vcpkg deps: arm64-v8a ====="
bash flutter/build_android_deps.sh arm64-v8a

echo "===== [2] vcpkg deps: armeabi-v7a ====="
bash flutter/build_android_deps.sh armeabi-v7a

echo "===== [3] cargo ndk: aarch64 ====="
bash flutter/ndk_arm64.sh

echo "===== [4] cargo ndk: armv7 ====="
bash flutter/ndk_arm.sh

echo "===== [5] copy to jniLibs ====="
mkdir -p flutter/android/app/src/main/jniLibs/arm64-v8a flutter/android/app/src/main/jniLibs/armeabi-v7a
cp target/aarch64-linux-android/release/liblibrustdesk.so flutter/android/app/src/main/jniLibs/arm64-v8a/librustdesk.so
cp target/armv7-linux-androideabi/release/liblibrustdesk.so flutter/android/app/src/main/jniLibs/armeabi-v7a/librustdesk.so

echo "===== [6] verify ====="
ls -la flutter/android/app/src/main/jniLibs/arm64-v8a/
ls -la flutter/android/app/src/main/jniLibs/armeabi-v7a/
echo "===== ALL DONE ====="