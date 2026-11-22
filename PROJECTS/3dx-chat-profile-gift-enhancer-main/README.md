This extension is designed to work exclusively on the [3DX Chat Profile Editor](https://status.3dxchat.net/profile-editor) page and is not active on any other sites. It will not interact with or affect any other web pages.

Below are instructions for installing the extension in Chrome and Firefox.

## What Does This Extension Do?

The 3DX Chat Profile Gift Enhancer extension adds a byte-counter to the bottom-left corner of the [3DX Chat Profile Editor](https://status.3dxchat.net/profile-editor) page, along with a convenient color management feature for enhanced user experience.

### Key Features:

-   **Byte Counter**: The existing character count often does not provide an accurate reflection when creating gifts, especially when using custom fonts or symbols that can be larger than a single byte. The extension’s byte-counter ensures that your gift content will fit within the 255-byte limit imposed by 3DX Chat.
-   **Color Management**: Users can easily save their preferred colors while using the profile editor. The extension allows users to select colors using the color picker and save them for later use. Saved colors are displayed in a dedicated section titled "Saved Colors", making it effortless to access and use them as needed. Each saved color text is clickable, allowing quick selection, and users can remove colors from their saved list as required.

### Screenshots

#### Gift preview with custom fonts and with byte limit in range

![OK](./demo/Screenshot%20-%20OK.jpg)

#### Gift preview with custom fonts and with byte limit exceeded

![ERROR](./demo/Screenshot%20-%20NOT%20OK.jpg)

#### Saved Colors Feature

![Saved Colors](./demo/Screenshot%20-%20Saved%20colors.jpg)

## Official Releases

-   Chrome: [https://chrome.google.com/webstore/detail/3dx-chat-profile-gift-edi/kfndddjjdnjkpfahoddjnkabbggpjcjl](https://chrome.google.com/webstore/detail/3dx-chat-profile-gift-edi/kfndddjjdnjkpfahoddjnkabbggpjcjl)
-   Firefox: [https://addons.mozilla.org/en-US/firefox/addon/3dx-chat-profile-gift-editor-e/](https://addons.mozilla.org/en-US/firefox/addon/3dx-chat-profile-gift-editor-e/)

## Installation Guide (Local Installation Only !)

### For Google Chrome

#### Step 1: Download the ZIP File

1. Go to the [releases page](https://github.com/PixelNini/3dx-chat-profile-gift-enhancer/releases).
2. Find the latest release and download the ZIP file to your local machine.

#### Step 2: Extract the ZIP File

1. Navigate to the location where you downloaded the ZIP file.
2. Right-click on the ZIP file and select 'Extract All...' or use your preferred method to extract the contents.

#### Step 3: Load the Extension into Chrome

1. Open the Google Chrome browser.
2. In the address bar, type `chrome://extensions/` and press Enter.
3. Turn on 'Developer mode' by toggling the switch in the top right corner.
4. Click the 'Load unpacked' button.
5. Navigate to the directory where you extracted the ZIP file and select the folder containing the extension files.
6. Click 'Select,' and the extension should now be loaded into your Chrome browser.

#### Step 4: Verify the Installation

1. You should now see the '3DX Chat Profile Gift Enhancer' extension listed in your extensions.
2. Verify it's enabled and visit the [3DX Chat Profile Editor](https://status.3dxchat.net/profile-editor) page, you should see the byte-counter once you clicked on `Gift preview`.

### For Firefox (Developer Edition Only)

> **Note:** The Firefox version of this extension is not signed. Therefore, it can only be installed in the Firefox Developer Edition.

#### Step 1: Download the ZIP File

Same as the Chrome instructions.

#### Step 2: Extract the ZIP File

Same as the Chrome instructions.

#### Step 3: Load the Extension into Firefox Developer Edition

1. Open Firefox Developer Edition.
2. In the address bar, type `about:debugging` and press Enter.
3. Click 'This Firefox' on the left side.
4. Click 'Load Temporary Add-on...' and navigate to the directory where you extracted the ZIP file.
5. Select the manifest file for the extension.
6. The extension should now be loaded into your Firefox Developer Edition browser.

## Troubleshooting

If you encounter any issues during installation, please [open an issue](https://github.com/PixelNini/3dx-chat-profile-gift-enhancer/issues) in this repository describing the problem, and I will do my best to assist you.

## License

This project is licensed under the CC0 1.0 Universal (CC0 1.0) Public Domain Dedication License - see the [LICENSE.md](LICENSE.md) file for details.

## Contributing

I welcome contributions! See the [CONTRIBUTING.md](CONTRIBUTING.md) file for how to get involved.
