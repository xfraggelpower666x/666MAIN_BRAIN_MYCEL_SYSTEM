package win

import (
	"fmt"
	"syscall"
	"unsafe"
)

var user32 = syscall.NewLazyDLL("user32.dll")
var shell32 = syscall.NewLazyDLL("shell32.dll")

func text(s string) *uint16 { value, _ := syscall.UTF16PtrFromString(s); return value }

func Message(title, message string, flags uintptr) uintptr {
	code, _, _ := user32.NewProc("MessageBoxW").Call(0, uintptr(unsafe.Pointer(text(message))), uintptr(unsafe.Pointer(text(title))), flags)
	return code
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
