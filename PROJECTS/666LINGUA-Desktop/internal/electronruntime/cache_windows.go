package electronruntime

import "lingua666/internal/win"

func lockCache() (func(), error) {
	return win.ElectronCacheLock()
}
