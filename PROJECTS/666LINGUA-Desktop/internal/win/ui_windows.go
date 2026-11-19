package win

import (
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"syscall"
	"time"
	"unsafe"
)

var user32 = syscall.NewLazyDLL("user32.dll")
var shell32 = syscall.NewLazyDLL("shell32.dll")

func text(s string) *uint16 { value, _ := syscall.UTF16PtrFromString(s); return value }

func Message(title, message string, flags uintptr) uintptr {
	code, _, _ := user32.NewProc("MessageBoxW").Call(0, uintptr(unsafe.Pointer(text(message))), uintptr(unsafe.Pointer(text(title))), flags)
	return code
}

// StartupError hinterlegt die Ursache auch bei einem Doppelklick ohne Konsole.
func StartupError(title, version string, err error) {
	message := strings.ReplaceAll(err.Error(), "\x00", "")
	if root, cacheErr := os.UserCacheDir(); cacheErr == nil {
		dir := filepath.Join(root, "666SOUNDsDESIGn", "666LINGUA", "logs")
		if os.MkdirAll(dir, 0700) == nil {
			if file, openErr := os.CreateTemp(dir, "startup-*.log"); openErr == nil {
				_, writeErr := fmt.Fprintf(file, "%s | %s %s | %s/%s\n%s\n", time.Now().Format(time.RFC3339), title, version, runtime.GOOS, runtime.GOARCH, message)
				closeErr := file.Close()
				if writeErr == nil && closeErr == nil {
					summary, _, _ := strings.Cut(message, "\n")
					message = summary + "\n\nProtokoll: " + file.Name()
				}
			}
		}
	}
	Message(title, message, 0x10)
}

func Open(path string) error {
	code, _, _ := shell32.NewProc("ShellExecuteW").Call(0, 0, uintptr(unsafe.Pointer(text(path))), 0, 0, 1)
	if code <= 32 {
		return fmt.Errorf("Windows konnte das Ziel nicht öffnen (Code %d).", code)
	}
	return nil
}

func DeleteAfterExit(path string, pid int) error {
	// Der Helfer hat ausschließlich Zugriff auf die explizit übergebenen Pfade.
	return startCleanup(path, pid)
}
