package win

import (
	"errors"
	"os"
	"os/exec"
	"runtime"
	"strconv"
	"syscall"
	"unsafe"
)

func Hidden(cmd *exec.Cmd) {
	cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true, CreationFlags: 0x08000000}
}

func PowerShell(script string, values ...string) error {
	cmd := exec.Command("powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script)
	cmd.Env = append(os.Environ(), values...)
	Hidden(cmd)
	return cmd.Run()
}

func startCleanup(path string, pid int) error {
	cmd := exec.Command("powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
		`Wait-Process -Id ([int]$env:LINGUA_EXIT_PID) -ErrorAction SilentlyContinue; Remove-Item -LiteralPath $env:LINGUA_EXIT_PATH -Force -ErrorAction SilentlyContinue; $p = Split-Path -LiteralPath $env:LINGUA_EXIT_PATH; if ((Test-Path -LiteralPath $p) -and -not (Get-ChildItem -LiteralPath $p -Force)) { Remove-Item -LiteralPath $p -ErrorAction SilentlyContinue }`)
	cmd.Env = append(os.Environ(), "LINGUA_EXIT_PID="+strconv.Itoa(pid), "LINGUA_EXIT_PATH="+path)
	Hidden(cmd)
	if err := cmd.Start(); err != nil {
		return err
	}
	return cmd.Process.Release()
}

var kernel32 = syscall.NewLazyDLL("kernel32.dll")

func SetupLock() (func(), error) {
	return namedLock("Local\\666LINGUA-Desktop-Setup-v1")
}

func namedLock(name string) (func(), error) {
	handle, _, err := kernel32.NewProc("CreateMutexW").Call(0, 0, uintptr(unsafe.Pointer(text(name))))
	if handle == 0 {
		return nil, err
	}
	runtime.LockOSThread()
	wait, _, _ := kernel32.NewProc("WaitForSingleObject").Call(handle, 10000)
	if wait != 0 && wait != 0x80 {
		_ = syscall.CloseHandle(syscall.Handle(handle))
		runtime.UnlockOSThread()
		return nil, errors.New("Ein anderer 666LINGUA-Vorgang hält die Sperre.")
	}
	return func() {
		kernel32.NewProc("ReleaseMutex").Call(handle)
		_ = syscall.CloseHandle(syscall.Handle(handle))
		runtime.UnlockOSThread()
	}, nil
}

func LearningLock() (func(), error) {
	return namedLock("Local\\666LINGUA-Desktop-Learning-v1")
}
