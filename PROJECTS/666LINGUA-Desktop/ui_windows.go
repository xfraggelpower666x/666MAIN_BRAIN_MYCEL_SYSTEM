package main

import (
	"io/fs"
	"os"
	"path/filepath"
	"strings"

	"github.com/wailsapp/wails/v2"
	"github.com/wailsapp/wails/v2/pkg/options"
	"github.com/wailsapp/wails/v2/pkg/options/assetserver"
	"github.com/wailsapp/wails/v2/pkg/options/windows"

	"lingua666/internal/win"
)

func showError(message string) { win.Message("666LINGUA", message, 0x10) }

func openExternal(url string) error { return win.Open(url) }

func openDesktopShare(address string) error {
	if text, ok := strings.CutPrefix(address, "https://wa.me/?text="); ok {
		return win.Open("whatsapp://send?text=" + text)
	}
	return openExternal(address)
}

func runDesktop(a *app, windowed bool) error {
	assets, err := fs.Sub(web, "app")
	if err != nil {
		return err
	}
	cache, err := os.UserCacheDir()
	if err != nil {
		return err
	}
	messages := windows.DefaultMessages()
	messages.MissingRequirements = "666LINGUA · WebView2"
	messages.InstallationRequired = "Die Windows-Komponente WebView2 fehlt. "
	messages.UpdateRequired = "Die Windows-Komponente WebView2 ist zu alt. "
	messages.PressOKToInstall = "Mit OK startet der Microsoft-Installer. Der Download benötigt Internet."
	messages.Webview2NotInstalled = "Die WebView2-Runtime ist nicht installiert."
	return wails.Run(&options.App{
		Title: "666LINGUA",
		Width: 1280, Height: 800, MinWidth: 480, MinHeight: 480,
		Fullscreen:       !windowed,
		BackgroundColour: options.NewRGB(5, 11, 27),
		AssetServer:      &assetserver.Options{Assets: assets, Middleware: a.desktopMiddleware(openDesktopShare)},
		Windows: &windows.Options{
			Theme:               windows.Dark,
			WebviewUserDataPath: filepath.Join(cache, "666SOUNDsDESIGn", "666LINGUA", "window"),
			Messages:            messages,
		},
	})
}
