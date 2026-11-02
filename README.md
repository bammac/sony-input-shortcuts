# Sony input shortcuts

Tiny Android TV apps that each switch a Sony TV to one HDMI input and then close. Give each device its own
tile, with its own name and picture, in place of Sony's plain "HDMI 1" icons. The tiles show up in the app
list, in any launcher's grid or dock, and in the "add app" list of Sony's own input menu.

![An example tile made with tools/make_tile.py](docs/example-tile.png)

- **One app per input.** Each is about 13 KB. It asks for no permissions, has no network access, and changes
  nothing on the TV. Uninstall it like any app.
- **It wakes the device.** When a CEC device is on the port, the app opens that device's input, which turns
  on an Apple TV or games console.
- **No logos are included.** Use images you own for your own TV, or make a text tile with
  `tools/make_tile.py`.

Tested on a Sony XR-83A90J (Android 12) and a Sony XR-65A95L (Android 14), both Google TV, in October 2026.
Other Sony Android TV and Google TV sets should work too, but their input IDs and TV app differ, so the guide
finds yours first.

## How to build it

Open [AGENT.md](AGENT.md) and follow it, or give this folder to a coding agent (Claude Code, Codex and others)
and ask it to follow that file. It covers:

1. Connecting ADB.
2. Finding your HDMI input IDs and the TV app that plays them.
3. Making one flavour and tile per device.
4. Building and installing.
5. Checking the tile on the TV.
6. Closing ADB again.

You need adb, JDK 17, Android SDK platform 34 with build-tools 34.0.0, and Python 3 with Pillow if you use
`tools/make_tile.py`.

## How it works

`OpenInputActivity` builds the passthrough channel URI for the input with
`TvContract.buildChannelUriForPassthroughInput` and sends `ACTION_VIEW` with
`vnd.android.cursor.item/channel` to the TV app. That is the same thing the TV's own input menu does. Then the
activity finishes. It uses `Theme.NoDisplay`, so nothing appears on screen.

Made alongside [cleanyourtv](https://github.com/Gathin23/cleanyourtv), but it works with any launcher.
Released under the [MIT licence](LICENSE).
