# Double Take

One picture in the thumbnail. Another when they click.

**https://deaeath.github.io/double-take/**

Pick a thumbnail picture and a click picture, and Double Take makes one PNG that shows each in its place. It all runs in your browser: your pictures never leave your device.

## How it works

A PNG can carry a gamma setting (its `gAMA` chunk). Browsers and many thumbnail makers apply it; some apps, like the 3DXChat client, ignore it. Double Take sets it to an extreme value, hides the thumbnail picture in near-white pixels that only that setting brings out, and puts the click picture in the pixels between them.

- Gamma applied: the click picture goes black and the thumbnail picture appears.
- Gamma ignored: the hidden picture fades into a light wash over the click picture.

It works wherever the thumbnail is made by something that applies the gamma setting before shrinking the picture. If a site strips the setting, both views show the click picture.

By KingColossus
