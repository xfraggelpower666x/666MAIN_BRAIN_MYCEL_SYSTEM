//go:build windows && installer

package main

import (
	"bufio"
	"bytes"
	_ "embed"
	"encoding/base64"
	"encoding/binary"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"time"
	"unicode/utf16"

	"lingua666/internal/electronruntime"
	"lingua666/internal/win"
)

//go:embed payload/666LINGUA.exe
var program []byte

const registry = `HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\666LINGUA`
const installVersion = "1.8.5"

//go:embed options_windows.ps1
var optionsScript string

type setupOptions struct {
	Root         string `json:"root"`
	PreviousRoot string `json:"previousRoot"`
	StartLink    string `json:"startLink"`
	DesktopLink  string `json:"desktopLink"`
	StartMenu    bool   `json:"startMenu"`
	Desktop      bool   `json:"desktop"`
	Launch       bool   `json:"launch"`
}

type locations struct {
	app, setup, link, desktop  string
	startMenu, desktopShortcut bool
	previousApp                string
}

func readOptions(readOnly bool) (*setupOptions, error) {
	systemRoot := os.Getenv("SystemRoot")
	if !filepath.IsAbs(systemRoot) {
		return nil, errors.New("Windows-Systempfad konnte nicht aufgelöst werden.")
	}
	units := utf16.Encode([]rune(optionsScript))
	data := make([]byte, 2*len(units))
	for i, unit := range units {
		binary.LittleEndian.PutUint16(data[2*i:], unit)
	}
	command := exec.Command(filepath.Join(systemRoot, "System32", "WindowsPowerShell", "v1.0", "powershell.exe"),
		"-NoProfile", "-STA", "-NonInteractive", "-EncodedCommand", base64.StdEncoding.EncodeToString(data))
	self, err := os.Executable()
	if err != nil {
		return nil, err
	}
	command.Env = append(os.Environ(), "LINGUA_SETUP_VERSION="+installVersion, "LINGUA_SETUP_READ_ONLY=0", "LINGUA_SETUP_EXE="+self)
	if readOnly {
		command.Env = append(command.Env, "LINGUA_SETUP_READ_ONLY=1")
	}
	win.WithoutConsole(command)
	out, err := setupDialogOutput(command)
	if err != nil {
		return nil, fmt.Errorf("Setup-Optionen konnten nicht geöffnet werden: %w", err)
	}
	raw := strings.TrimSpace(strings.TrimPrefix(string(out), "\ufeff"))
	if raw == "" {
		return nil, nil
	}
	var o setupOptions
	if err := json.Unmarshal([]byte(raw), &o); err != nil {
		return nil, fmt.Errorf("Setup-Auswahl konnte nicht gelesen werden: %w", err)
	}
	return &o, nil
}

func setupDialogOutput(command *exec.Cmd) ([]byte, error) {
	output, err := command.StdoutPipe()
	if err != nil {
		return nil, err
	}
	defer output.Close()
	var stdout, stderr bytes.Buffer
	command.Stderr = &stderr
	if err := command.Start(); err != nil {
		return nil, err
	}
	visible := make(chan struct{}, 1)
	done := make(chan error, 1)
	go func() {
		scanner := bufio.NewScanner(output)
		scanner.Buffer(make([]byte, 4096), 256000)
		for scanner.Scan() {
			if scanner.Text() == "LINGUA_SETUP_VISIBLE" {
				select {
				case visible <- struct{}{}:
				default:
				}
			} else {
				stdout.WriteString(scanner.Text())
				stdout.WriteByte('\n')
			}
		}
		scanErr := scanner.Err()
		if scanErr != nil {
			_ = command.Process.Kill()
		}
		done <- errors.Join(scanErr, command.Wait())
	}()
	timer := time.NewTimer(60 * time.Second)
	defer timer.Stop()
	select {
	case <-visible:
		err = <-done
	case err = <-done:
	case <-timer.C:
		_ = command.Process.Kill()
		err = errors.Join(errors.New("Der Windows-Setup-Dialog wurde nach 60 Sekunden nicht sichtbar."), <-done)
	}
	if err != nil {
		if detail := strings.TrimSpace(stderr.String()); detail != "" {
			return nil, fmt.Errorf("%w\nPowerShell: %s", err, detail)
		}
		return nil, err
	}
	return stdout.Bytes(), nil
}

func (o setupOptions) paths() (locations, error) {
	root := filepath.Clean(o.Root)
	if !filepath.IsAbs(root) || filepath.Dir(root) == root ||
		strings.HasPrefix(root, `\\?\`) || strings.HasPrefix(root, `\\.\`) {
		return locations{}, errors.New("Bitte einen vollständigen Installationspfad mit eigenem Unterordner auswählen.")
	}
	for _, link := range []string{o.StartLink, o.DesktopLink} {
		if link != "" && (!filepath.IsAbs(link) || !strings.EqualFold(filepath.Base(link), "666LINGUA.lnk")) {
			return locations{}, errors.New("Ein Verknüpfungspfad ist ungültig.")
		}
	}
	var previousApp string
	if filepath.IsAbs(o.PreviousRoot) {
		previousApp = filepath.Join(o.PreviousRoot, "666LINGUA.exe")
	}
	return locations{
		app: filepath.Join(root, "666LINGUA.exe"), setup: filepath.Join(root, "666LINGUA-Uninstall.exe"),
		link: o.StartLink, desktop: o.DesktopLink, startMenu: o.StartMenu, desktopShortcut: o.Desktop, previousApp: previousApp,
	}, nil
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
	file, stub, archive, err := electronruntime.OpenPayload(self)
	if err != nil {
		return fmt.Errorf("Setup ist unvollständig: %w", err)
	}
	defer file.Close()
	// Die Deinstallation benötigt nur das Programm, nicht das eingebettete Archiv.
	installer, err := io.ReadAll(stub)
	if err != nil {
		return err
	}
	original := map[string][]byte{}
	for _, path := range []string{p.app, p.setup, p.link, p.desktop} {
		if path == "" {
			continue
		}
		data, err := os.ReadFile(path)
		if err != nil && !errors.Is(err, os.ErrNotExist) {
			return err
		}
		original[path] = data
	}
	rollbackRuntime, err := installRuntime(filepath.Dir(p.app), archive)
	if err != nil {
		return err
	}
	err = writeInstall(p, installer)
	if err == nil {
		return nil
	}
	rollbackRuntime()
	// Bestehende Dateien nach einem fehlgeschlagenen Update zurückholen.
	var rollback []error
	for _, path := range []string{p.app, p.setup, p.link, p.desktop} {
		if path == "" {
			continue
		}
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
	return errors.Join(append([]error{err}, rollback...)...)
}

func installRuntime(root string, archive io.Reader) (func(), error) {
	d := electronruntime.WindowsX64()
	target := filepath.Join(root, d.Name)
	removeArchive := func() {}
	_, statErr := os.Stat(target)
	if errors.Is(statErr, os.ErrNotExist) {
		if err := d.Save(archive, target); err != nil {
			return nil, err
		}
		removeArchive = func() { _ = os.Remove(target) }
	} else if statErr != nil {
		return nil, statErr
	} else if err := d.Verify(target); err != nil {
		return nil, fmt.Errorf("Im Zielordner liegt bereits ein abweichendes Electron-Archiv. %w", err)
	}
	cache, err := electronruntime.CacheDir()
	if err == nil {
		_, err = d.Prepare(target, cache)
	}
	if err != nil {
		removeArchive()
		return nil, err
	}
	return removeArchive, nil
}

func writeInstall(p locations, installer []byte) error {
	if err := replace(p.app, program); err != nil {
		return fmt.Errorf("Programmdatei konnte nicht geschrieben werden. Bei einem Update 666LINGUA vorher schließen. %w", err)
	}
	if err := replace(p.setup, installer); err != nil {
		return err
	}
	if err := updateShortcut(p.link, p.app, p.previousApp, p.startMenu); err != nil {
		return fmt.Errorf("Startmenü-Verknüpfung: %w", err)
	}
	if err := updateShortcut(p.desktop, p.app, p.previousApp, p.desktopShortcut); err != nil {
		return fmt.Errorf("Desktop-Verknüpfung: %w", err)
	}
	return win.PowerShell(`$ErrorActionPreference='Stop'
$path='HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\666LINGUA'
$old=Get-ItemProperty -LiteralPath $path -ErrorAction SilentlyContinue
$values=@{DisplayName='666LINGUA'; DisplayVersion=$env:LINGUA_VERSION; Publisher='666SOUNDsDESIGn'; InstallLocation=(Split-Path -LiteralPath $env:LINGUA_APP); DisplayIcon=$env:LINGUA_APP; UninstallString=('"'+$env:LINGUA_UNINSTALL+'" --uninstall'); StartMenuShortcut=[string]$env:LINGUA_START_LINK; DesktopShortcut=[string]$env:LINGUA_DESKTOP_LINK}
try {
    if (!$old) { [void](New-Item -Path $path -Force) }
    foreach($name in $values.Keys) { [void](New-ItemProperty -LiteralPath $path -Name $name -Value $values[$name] -PropertyType String -Force) }
    $stored=Get-ItemProperty -LiteralPath $path
    foreach($name in $values.Keys) {
        if ($stored.$name -cne $values[$name]) { throw "Installationsregister: $name konnte nicht verifiziert werden." }
    }
} catch {
    if (!$old) { Remove-Item -LiteralPath $path -ErrorAction SilentlyContinue }
    else {
        foreach($name in $values.Keys) {
            if ($old.PSObject.Properties[$name]) { [void](New-ItemProperty -LiteralPath $path -Name $name -Value $old.$name -PropertyType String -Force) }
            else { Remove-ItemProperty -LiteralPath $path -Name $name -ErrorAction SilentlyContinue }
        }
    }
    throw
}`,
		"LINGUA_APP="+p.app, "LINGUA_UNINSTALL="+p.setup, "LINGUA_VERSION="+installVersion,
		"LINGUA_START_LINK="+p.link, "LINGUA_DESKTOP_LINK="+p.desktop)
}

// Eine gleichnamige fremde Verknüpfung bleibt erhalten.
func updateShortcut(link, app, previousApp string, create bool) error {
	if link == "" {
		return nil
	}
	createLink := "0"
	if create {
		createLink = "1"
	}
	return win.PowerShell(`$ErrorActionPreference='Stop'
$link=$env:LINGUA_LINK
$existing=Test-Path -LiteralPath $link
if (!$existing -and $env:LINGUA_LINK_CREATE -ne '1') { return }
$shortcut=(New-Object -ComObject WScript.Shell).CreateShortcut($link)
if ($existing -and $shortcut.TargetPath -ne $env:LINGUA_APP -and $shortcut.TargetPath -ne $env:LINGUA_PREVIOUS_APP) {
    if ($env:LINGUA_LINK_CREATE -eq '1') { throw 'Eine andere Verknüpfung nutzt diesen Namen.' }
    return
}
if ($env:LINGUA_LINK_CREATE -ne '1') { Remove-Item -LiteralPath $link; return }
[void][IO.Directory]::CreateDirectory((Split-Path -LiteralPath $link))
$shortcut.TargetPath=$env:LINGUA_APP
$shortcut.WorkingDirectory=(Split-Path -LiteralPath $env:LINGUA_APP)
$shortcut.Description='666LINGUA'
$shortcut.Save()`,
		"LINGUA_LINK="+link, "LINGUA_APP="+app, "LINGUA_PREVIOUS_APP="+previousApp, "LINGUA_LINK_CREATE="+createLink)
}

func uninstall(p locations, registered bool) error {
	if err := os.Remove(p.app); err != nil && !errors.Is(err, os.ErrNotExist) {
		return fmt.Errorf("Bitte 666LINGUA schließen. %w", err)
	}
	if registered {
		for _, link := range []string{p.link, p.desktop} {
			if err := updateShortcut(link, p.app, "", false); err != nil {
				return err
			}
		}
		if err := reg("delete", registry, "/f"); err != nil {
			return err
		}
	}
	d := electronruntime.WindowsX64()
	archive := filepath.Join(filepath.Dir(p.app), d.Name)
	if d.Verify(archive) == nil {
		if err := os.Remove(archive); err != nil {
			return err
		}
	}
	return win.DeleteAfterExit(p.setup, os.Getpid())
}

func withSetupLock(operation func() error) error {
	release, err := win.SetupLock()
	if err != nil {
		return err
	}
	defer release()
	return operation()
}

func run() error {
	title := "666LINGUA Setup · " + runtime.GOARCH
	switch {
	case len(os.Args) == 2 && os.Args[1] == "--uninstall":
		self, err := os.Executable()
		if err != nil {
			return err
		}
		if !strings.EqualFold(filepath.Base(self), "666LINGUA-Uninstall.exe") {
			return errors.New("Die Deinstallation bitte über die Windows-Einstellungen starten.")
		}
		o, err := readOptions(true)
		if err != nil {
			return err
		}
		if o == nil {
			return errors.New("Der Installationsstatus konnte nicht gelesen werden.")
		}
		root := filepath.Dir(self)
		registered := o.PreviousRoot != "" && strings.EqualFold(root, filepath.Clean(o.PreviousRoot))
		o.Root = root
		p, err := o.paths()
		if err != nil {
			return err
		}
		if win.Message(title, "666LINGUA deinstallieren? Deine Einstellungen und bestätigten Übersetzungen bleiben im Benutzerprofil.", 0x24) != 6 {
			return nil
		}
		if err := withSetupLock(func() error { return uninstall(p, registered) }); err != nil {
			return err
		}
		win.Message(title, "666LINGUA wurde deinstalliert.", 0x40)
		return nil
	case len(os.Args) == 1:
		o, err := readOptions(false)
		if err != nil || o == nil {
			return err
		}
		p, err := o.paths()
		if err != nil {
			return err
		}
		if err := withSetupLock(func() error { return install(p) }); err != nil {
			return err
		}
		if o.Launch {
			win.Message(title, "Installation abgeschlossen.", 0x40)
			if err := win.Open(p.app); err != nil {
				win.Message(title, "Installation abgeschlossen. "+err.Error(), 0x30)
			}
		} else {
			win.Message(title, "Installation abgeschlossen.\n\nZiel: "+o.Root, 0x40)
		}
		return nil
	default:
		return errors.New("Unbekannter Setup-Parameter.")
	}
}

func main() {
	if err := run(); err != nil {
		win.StartupError("666LINGUA Setup", installVersion, err)
		os.Exit(1)
	}
}
