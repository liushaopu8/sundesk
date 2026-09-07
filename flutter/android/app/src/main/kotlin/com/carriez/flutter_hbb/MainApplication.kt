package com.carriez.flutter_hbb

import android.app.Application
import android.util.Log
import com.sunyard.exception.SDKException
import com.sunyard.smartposapi.DeviceMaster
import ffi.FFI

class MainApplication : Application() {
    companion object {
        private const val TAG = "MainApplication"
    }

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "App start")
        FFI.onAppStart(applicationContext)
        try {
            DeviceMaster.getInstance().init(this)
        } catch (e: SDKException) {
            throw RuntimeException(e)
        }
    }
}
