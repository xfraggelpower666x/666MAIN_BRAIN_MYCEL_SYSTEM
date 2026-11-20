package electronruntime

import "sync"

var cacheMutex sync.Mutex

func lockCache() (func(), error) {
	cacheMutex.Lock()
	return cacheMutex.Unlock, nil
}
