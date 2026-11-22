package com.example.htmlapp;

import android.app.Activity;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.net.Uri;

public class MainActivity extends Activity {
    private WebView webView;
    private FrameLayout root;
    private View customView;
    private WebChromeClient.CustomViewCallback customViewCallback;
    private static final String START_PAGE = "%%ENTRY_FILE%%";

    @Override
    public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_HARDWARE_ACCELERATED,
                WindowManager.LayoutParams.FLAG_HARDWARE_ACCELERATED);

        root = new FrameLayout(this);
        webView = new WebView(this);
        root.addView(webView, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));
        setContentView(root);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setJavaScriptCanOpenWindowsAutomatically(true);
        settings.setSupportMultipleWindows(false);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setMediaPlaybackRequiresUserGesture(false);

        // Keep local site files accessible while avoiding broad cross-origin file access.
        if (Build.VERSION.SDK_INT >= 16) {
            settings.setAllowFileAccessFromFileURLs(false);
            settings.setAllowUniversalAccessFromFileURLs(false);
        }

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onShowCustomView(View view, CustomViewCallback callback) {
                if (customView != null) {
                    callback.onCustomViewHidden();
                    return;
                }
                customView = view;
                customViewCallback = callback;
                webView.setVisibility(View.GONE);
                root.addView(customView, new FrameLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.MATCH_PARENT));
            }

            @Override
            public void onHideCustomView() {
                hideCustomView();
            }
        });

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                Uri uri = Uri.parse(url);
                return !"file".equals(uri.getScheme());
            }
        });
        webView.loadUrl("file:///android_asset/site/" + START_PAGE);
    }

    private void hideCustomView() {
        if (customView == null) return;
        root.removeView(customView);
        customView = null;
        webView.setVisibility(View.VISIBLE);
        if (customViewCallback != null) {
            customViewCallback.onCustomViewHidden();
            customViewCallback = null;
        }
    }

    @Override
    public void onBackPressed() {
        if (customView != null) {
            hideCustomView();
        } else if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.destroy();
            webView = null;
        }
        super.onDestroy();
    }
}
