//go:build windows && installer

package main

import (
	_ "embed"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"

	"lingua666/internal/win"
)

//go:embed payload/666LINGUA.exe
var program []byte

const registry = `HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\666LINGUA`
const installVersion = "1.5.2"

type locations struct{ app, setup, link string }

func paths() (locations, error) {
	local, roam := os.Getenv("LOCALAPPDATA"), os.Getenv("APPDATA")
	if !filepath.IsAbs(local) || !filepath.IsAbs(roam) {
		return locations{}, errors.New("Windows-Benutzerpfade konnten nicht aufgelöst werden.")
	}
	root := filepath.Join(local, "Programs", "666LINGUA")
	link := filepath.Join(roam, "Microsoft", "Windows", "Start Menu", "Programs", "666LINGUA.lnk")
	return locations{filepath.Join(root, "666LINGUA.exe"), filepath.Join(root, "666LINGUA-Uninstall.exe"), link}, nil
}

func reg(args ...string) error {
	command := exec.Command("reg.exe", args...)
	win.Hidden(command)
	b, err := command.CombinedOutput()
	if err != nil {
		return fmt.Errorf("Windows-Installationsregister: %w (%s)", err, string(b))
	}
	return nil
}

func replace(path string, content []byte) error {
	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0700); err != nil {
		return err
	}
	temp, err := os.CreateTemp(dir, ".666lingua-*.tmp")
	if err != nil {
		return err
	}
	defer os.Remove(temp.Name())
	_, err = temp.Write(content)
	if err == nil {
		err = temp.Sync()
	}
	closeErr := temp.Close()
	if err != nil {
		return err
	}
	if closeErr != nil {
		return closeErr
	}
	return os.Rename(temp.Name(), path)
}

func install(p locations) error {
	self, err := os.Executable()
	if err != nil {
		return err
	}
	installer, err := os.ReadFile(self)
	if err != nil {
		return err
	}
	original := map[string][]byte{}
	for _, path := range []string{p.app, p.setup, p.link} {
		data, err := os.ReadFile(path)
		if err != nil && !errors.Is(err, os.ErrNotExist) {
			return err
		}
		original[path] = data
	}
	err = writeInstall(p, installer)
	if err == nil {
		return nil
	}
	// Bestehende Dateien nach einem fehlgeschlagenen Update zurückholen.
	var rollback []error
	for _, path := range []string{p.app, p.setup, p.link} {
		prior := original[path]
		if prior == nil {
			if e := os.Remove(path); e != nil && !errors.Is(e, os.ErrNotExist) {
				rollback = append(rollback, e)
			}
		} else {
			if current, e := os.ReadFile(path); e == nil && string(current) == string(prior) {
				continue
			}
			if e := replace(path, prior); e != nil {
				rollback = append(rollback, e)
			}
		}
	}
	if original[p.app] == nil {
		_ = reg("delete", registry, "/f")
	}
	return errors.Join(append([]error{err}, rollback...)...)
}

func writeInstall(p locations, installer []byte) error {
	if err := replace(p.app, program); err != nil {
		return fmt.Errorf("Programmdatei konnte nicht geschrieben werden. Bei einem Update 666LINGUA vorher schließen. %w", err)
	}
	if err := replace(p.setup, installer); err != nil {
		return err
	}
	err := win.PowerShell(`$ErrorActionPreference='Stop'; $s=(New-Object -ComObject WScript.Shell).CreateShortcut($env:LINGUA_LINK); $s.TargetPath=$env:LINGUA_APP; $s.WorkingDirectory=(Split-Path -LiteralPath $env:LINGUA_APP); $s.Description='666LINGUA'; $s.Save()`,
		"LINGUA_LINK="+p.link, "LINGUA_APP="+p.app)
	if err != nil {
		return fmt.Errorf("Startmenü-Verknüpfung konnte nicht erstellt werden: %w", err)
	}
	values := [][2]string{{"DisplayName", "666LINGUA"}, {"DisplayVersion", installVersion}, {"Publisher", "666SOUNDsDESIGn"},
		{"InstallLocation", filepath.Dir(p.app)}, {"DisplayIcon", p.app}, {"UninstallString", `"` + p.setup + `" --uninstall`}}
	for _, value := range values {
		if err := reg("add", registry, "/v", value[0], "/t", "REG_SZ", "/d", value[1], "/f"); err != nil {
			return err
		}
	}
	return nil
}

func uninstall(p locations) error {
	if err := os.Remove(p.app); err != nil && !errors.Is(err, os.ErrNotExist) {
		return fmt.Errorf("Bitte 666LINGUA schließen. %w", err)
	}
	if err := os.Remove(p.link); err != nil && !errors.Is(err, os.ErrNotExist) {
		return err
	}
	if reg("query", registry) == nil {
		if err := reg("delete", registry, "/f"); err != nil {
			return err
		}
	}
	return win.DeleteAfterExit(p.setup, os.Getpid())
}

func main() {
	title := "666LINGUA Setup · " + runtime.GOARCH
	p, err := paths()
	if err != nil {
		win.Message(title, err.Error(), 0x10)
		os.Exit(1)
	}
	release, err := win.SetupLock()
	if err != nil {
		win.Message(title, err.Error(), 0x10)
		os.Exit(1)
	}
	defer release()
	switch {
	case len(os.Args) == 2 && os.Args[1] == "--uninstall":
		if win.Message(title, "666LINGUA deinstallieren? Bestätigte Übersetzungen bleiben im Benutzerprofil.", 0x24) != 6 {
			return
		}
		err = uninstall(p)
		if err == nil {
			win.Message(title, "666LINGUA wurde deinstalliert.", 0x40)
			return
		}
	case len(os.Args) == 1:
		if win.Message(title, "666LINGUA "+installVersion+" für diesen Windows-Benutzer installieren?\n\nZiel: "+filepath.Dir(p.app), 0x24) != 6 {
			return
		}
		err = install(p)
		if err == nil {
			if win.Message(title, "Installation abgeschlossen. 666LINGUA jetzt öffnen?", 0x24) == 6 {
				if openErr := win.Open(p.app); openErr != nil {
					win.Message(title, "Installation abgeschlossen. "+openErr.Error(), 0x30)
				}
			}
			return
		}
	default:
		err = errors.New("Unbekannter Setup-Parameter.")
	}
	win.Message(title, err.Error(), 0x10)
	os.Exit(1)
}
