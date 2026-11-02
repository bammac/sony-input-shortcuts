package local.inputshortcut;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.media.tv.TvContract;
import android.media.tv.TvInputInfo;
import android.media.tv.TvInputManager;
import android.net.Uri;
import android.os.Bundle;
import android.widget.Toast;

/** Switches the TV to one input, the way the TV's own input menu does, then closes. */
public class OpenInputActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        final String port = BuildConfig.INPUT_ID;
        String target = port;
        // A CEC device on this port is a child input of it; opening the child also makes it the active source,
        // which wakes the device (an Apple TV or a games console, for example).
        TvInputManager tim = (TvInputManager) getSystemService(TV_INPUT_SERVICE);
        if (tim != null) {
            try {
                for (TvInputInfo info : tim.getTvInputList()) {
                    if (port.equals(info.getParentId())) {
                        target = info.getId();
                        break;
                    }
                }
            } catch (RuntimeException ignored) {
            }
        }
        Uri uri = TvContract.buildChannelUriForPassthroughInput(target);
        Intent view = new Intent(Intent.ACTION_VIEW).setDataAndType(uri, "vnd.android.cursor.item/channel")
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        try {
            if (BuildConfig.TV_APP.isEmpty()) {
                startActivity(view);
            } else {
                startActivity(new Intent(view).setPackage(BuildConfig.TV_APP));
            }
        } catch (ActivityNotFoundException | SecurityException e) {
            try {
                startActivity(view);
            } catch (ActivityNotFoundException | SecurityException e2) {
                Toast.makeText(this, "Input not available", Toast.LENGTH_SHORT).show();
            }
        }
        finish();
    }
}
