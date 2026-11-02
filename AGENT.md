# Input shortcut apps for a Sony Google TV / Android TV

Give this folder to a coding agent (Claude Code, Codex and others) and ask it to follow this file.

**What you get:** tiny "apps" that each switch the TV to one HDMI input and close. For example, a "Games Console"
tile goes straight to HDMI 1. They appear in the app list, in any launcher, and in the "add app" list of Sony's own
input menu. Each one is about 13 KB, has no permissions and no network access, and changes nothing on the TV. Delete it
like any app.

**Tested on:** a Sony XR-83A90J (Android 12) and a Sony XR-65A95L (Android 14), Google TV, October 2026. Other
Sony Android TV and Google TV sets should work the same way, but their input IDs and TV app differ. Step 2 and
step 3 find them, so never copy the example values blindly.

---

## Instructions for the agent

Follow the steps in order, and show the person what you found at each one. Ask before anything that is theirs to
decide: which devices, the names, the colours and the images.

### Rules

- **Change nothing on the TV but installing these apps.** Don't disable, uninstall or change settings or other apps.
  Don't start factory or service menus or any package you don't recognise.
- **Images:** use only images the person gives you, for their own TV. The template contains no brand logos. If the
  person has no image, make a text tile (step 4). Don't download logos from the web for them, and don't put
  other companies' logos in anything they share publicly.
- **Close ADB at the end** (step 7). Port 5555 is unencrypted, so leaving it open on a home network is a real risk.
- **Keep nothing identifying in files** you write or share: no IP addresses, Wi-Fi names, serial numbers or ADB keys.

### Step 0: what you need on the computer

- `adb`, from Android platform-tools.
- JDK 17.
- Android SDK command-line tools with `platforms;android-34` and `build-tools;34.0.0`. Point `ANDROID_HOME` at the
  SDK, or write `sdk.dir=...` in `local.properties`.
- Python 3 with Pillow (`pip install pillow`). Only `tools/make_tile.py` needs it.

On a Mac with Homebrew: `brew install openjdk@17 android-platform-tools` and
`brew install --cask android-commandlinetools`. Then run
`sdkmanager "platforms;android-34" "build-tools;34.0.0"` and set `JAVA_HOME=/opt/homebrew/opt/openjdk@17`.

### Step 1: connect ADB

Ask the person to open **Settings > System > About** on the TV and select **Android TV OS build** seven times. That
turns on Developer options. Then, in **Settings > System > Developer options**:

- **Android 11 and later with "Wireless debugging"** (for example the A95L):
  1. Turn on **USB debugging** and **Wireless debugging**.
  2. Open **Pair device with pairing code** and run `adb pair <tv ip>:<pairing port> <code>`.
  3. Run `adb mdns services` (or read the IP:port on the Wireless debugging screen), then `adb connect <tv ip>:<port>`.
- **Older Sony sets with an "ADB debugging" toggle** (for example the A90J): turn on **USB debugging** and **ADB
  debugging**, then `adb connect <tv ip>:5555`.

Accept "Allow USB debugging?" on the TV. Check with `adb devices`, which should list the TV as `device`. If `adb pair`
hangs, run `adb kill-server` and try again. Wireless debugging switches itself off when the TV restarts or Wi-Fi drops,
so pair again if that happens.

On macOS, a sandboxed agent may be refused network access to the TV ("No route to host") by Local Network privacy.
Run adb from the person's own terminal in that case.

### Step 2: find the HDMI inputs

```bash
adb shell dumpsys tv_input | grep -E 'TvInputHardwareInfo \{id|^ +[0-9]+: com\.' | sort -u
adb shell dumpsys hdmi_control | grep -E 'CEC: logical_address'
```

The first command shows lines like `TvInputHardwareInfo {id=4, ... hdmi_port=3, ...}` and a map like
`4: com.mediatek.external/.HdmiInputService/HW4`. Join them on the id: **hardware id 4 is HDMI 3, and its input ID is
`.../HW4`**. Make a table for the person showing each HDMI port and its input ID. Use the hardware input (`.../HWn`) of
the **port**, not a CEC child input such as `.../HDMI300004`. The app finds the CEC child itself, which wakes the device.

The second command lists CEC devices by name and `port_id`. That helps the person see what is plugged into which
port, but not every device supports CEC.

What we saw (check yours):

| TV | Input ID pattern | HDMI 1 to 4 |
|---|---|---|
| XR-83A90J, Android 12 | `com.sony.dtv.tvinput.external/.ExternalTvInputService/HWn` | HW2 to HW5 |
| XR-65A95L, Android 14 | `com.mediatek.external/.HdmiInputService/HWn` | HW2 to HW5 |

### Step 3: find the TV app that plays an input

```bash
adb shell cmd package query-activities --brief -a android.intent.action.VIEW \
  -d 'content://android.media.tv/passthrough/<input ID with each / written as %2F>' \
  -t vnd.android.cursor.item/channel
```

For example, with `com.mediatek.external%2F.HdmiInputService%2FHW4` you should get one activity. Its package is
`TV_APP`: we saw `com.sony.dtv.tvx` on the A90J and `com.sony.dtv.tvlin` on the A95L. If several packages answer,
pick the Sony one. Another launcher may claim the channel type too.

### Step 4: make one app per device

Ask the person for each device's **name**, **HDMI port**, and **image or colour**. Then, in this folder:

1. In `app/build.gradle`, set `TV_APP` to the package from step 3. Copy the `example` block once per device, give
   each a short lowercase flavour name and its own `applicationId` (`local.inputshortcut.<name>`), and set its
   `INPUT_ID` from step 2. Delete the `example` block and `app/src/example/` when you're done.
2. For each flavour, create `app/src/<name>/res/values/strings.xml` with `app_name`, which is the label shown under
   the tile.
3. Make its tile images:
   ```bash
   python3 tools/make_tile.py app/src/<name>/res/drawable-nodpi --text "Games Console" --bg "#D32D26"
   python3 tools/make_tile.py app/src/<name>/res/drawable-nodpi --image their-logo.png --bg "#F5F5F7" --scale 0.7
   python3 tools/make_tile.py app/src/<name>/res/drawable-nodpi --image their-logo.png --bg "#CCCECF" --bg2 "#EDEEEF"
   ```
   The result is `banner.png` (320x180, the TV tile) and `icon.png`. Open `banner.png` and show the person. Adjust
   `--scale` if the logo looks too big or too small. Pillow can't read SVG, so convert it to PNG first, for example
   by opening it in a browser and taking a screenshot, or with `rsvg-convert`.

### Step 5: build and install

```bash
./gradlew --no-daemon assemble<Name>Release            # e.g. assembleConsoleRelease; assembleRelease builds all
adb install -r app/build/outputs/apk/<name>/release/app-<name>-release.apk
```

The release build is signed with the SDK's debug key. That is fine for sideloading onto your own TV.

### Step 6: check it on the TV

```bash
adb shell am start -n local.inputshortcut.<name>/local.inputshortcut.OpenInputActivity
sleep 5
adb shell dumpsys tv_input | grep -A1 'SessionState@'
adb shell input keyevent HOME
```

`inputId:` should be that port's `.../HWn`, or its CEC child (`.../HDMI...`) when a CEC device is plugged in. The
picture switches as well. Note that `adb exec-out screencap` gives a black image for HDMI, so the screenshot can't
prove it. Then ask the person to open the tile with the real remote.

**Adding a tile to Sony's own input menu:** open the input menu, go to the edit or **+** option, and add the app. If
Sony says *"Edit is not available when an accessibility feature is turned on"*, an accessibility service is running.
That could be a remote-button helper, a custom launcher's key helper, or TalkBack. The person turns it off under
**Settings > System > Accessibility**, edits the menu, then turns it back on.

### Step 7: close ADB

1. On the TV, in **Developer options**, turn off **Wireless debugging** or **ADB debugging**, and **USB debugging**.
2. Choose **Revoke USB debugging authorisations**, then restart the TV.
3. From the computer, check the port is shut: `nc -vz -G 3 <tv ip> 5555` (macOS) or `nc -vz -w 3 <tv ip> 5555`
   (Linux). It must be **refused**.

**Sony quirk (seen on the A90J):** turning the toggles off left ADB listening on 5555, even after a restart. If the
port is still open, connect once more and run `adb shell settings put global adb_enabled 0`. The connection drops as it
takes effect. Restart the TV and check again.

### Changing or removing later

- Move a tile to another port: change its `INPUT_ID`, then rebuild and reinstall (steps 5 and 6).
- Rename: change `app_name`, then rebuild.
- Remove: `adb uninstall local.inputshortcut.<name>`, or use Settings > Apps on the TV.
