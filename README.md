# HTML to APK Offline Converter

A Windows desktop utility that packages HTML5 websites and projects (HTML5, CSS3, JavaScript, images, fonts, audio and video files) into an Android WebView project. Website files are copied into the APK so local assets can work offline. JavaScript, DOM storage, hardware acceleration and fullscreen HTML5 media are enabled.

## Build the Windows EXE
GitHub Actions builds a portable EXE on every push. Open **Actions → Build applications → Artifacts** and download \`HTML-to-APK-Windows\`.

## Use
1. Start \`HTML-to-APK.exe\`.
2. Choose an HTML file, a website folder, or a ZIP archive.
3. Set the app name, package ID, and minimum Android version.
4. Choose an output folder and press **Create Android project**.
5. To build the APK locally, install JDK 17, Android SDK Platform 35 / Build Tools 35.0.0 and Gradle 8.7; set \`ANDROID_HOME\` and run **Build APK** in the app.

The desktop converter itself works offline. First-time Android toolchain installation requires internet; after SDK/Gradle are installed and cached, builds can run offline with Gradle's offline option.

## Android compatibility
The template uses minSdk 14 (Android 4.0) and compileSdk 35. The WebView enables JavaScript, DOM storage, HTML5 audio/video playback and fullscreen media. Support for Canvas, SVG, CSS3 and newer JavaScript APIs depends on the WebView installed on the device. Android 4.x WebView is old and cannot render every modern HTML5 feature; Android 5.0+ is recommended for better compatibility. The selected minimum is a compatibility floor, not a promise that modern website APIs exist on old devices. Android 4.0 is API 14; Android 4.1 is API 16.

## GitHub Actions
The workflow builds:
- Windows portable EXE
- A sample offline WebView APK from the Android template

The sample APK is a demonstration shell. To package your own website, use the EXE to create a project and build that project with the Android SDK.

## Security
Only package HTML files you trust. Local JavaScript is enabled so interactive websites work. External links are opened inside the WebView; network permission is not included by default.
