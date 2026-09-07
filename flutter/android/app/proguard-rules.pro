# Keep class members from protobuf generated code.
-keepclassmembers class * extends com.google.protobuf.GeneratedMessageLite {
  <fields>;
}

# Keep rustls-platform-verifier classes for JNI
-keep, includedescriptorclasses class org.rustls.platformverifier.** { *; }

# SunDesk: keep the whole Sunyard smartposapi SDK. Its native .so accesses
# Java fields/methods by name via JNI (e.g. NativeTransfer.mNativePtr) and it
# uses AIDL stubs against the device framework; obfuscating these breaks init
# with NoSuchFieldError / ClassCastException at DeviceMaster.init().
-keep class com.sunyard.** { *; }
-keep interface com.sunyard.** { *; }
-keepclassmembers class com.sunyard.** {
    native <methods>;
    <fields>;
}
-dontwarn com.sunyard.**

# SunDesk: the SDK also ships an AIDL interface in the android.app package
# (android.app.SunSDKManagers + Stub/Proxy) which it casts the system service
# to. Keep it or R8 renames it and the cast fails at runtime.
-keep class android.app.SunSDKManagers** { *; }
-keep interface android.app.SunSDKManagers** { *; }
