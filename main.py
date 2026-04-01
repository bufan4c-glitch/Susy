name: Build for Android

on:
  push:
    branches: [ main, головний ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Build with Buildozer
        uses: pypa/buildozer-action@v1
        with:
          command: buildozer android debug
          buildozer_version: stable

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: package
          path: bin/*.apk
