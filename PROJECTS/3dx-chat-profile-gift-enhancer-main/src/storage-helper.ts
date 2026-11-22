import browser from 'webextension-polyfill';

export class StorageHelper {
    private storageArea: browser.Storage.StorageArea;

    constructor(area: 'sync' | 'local' = 'local') {
        this.storageArea = browser.storage[area];
    }

    async get<T>(key: string): Promise<T | undefined> {
        const result = await this.storageArea.get(key);
        return result[key] as T;
    }

    async set<T>(key: string, value: T): Promise<void> {
        await this.storageArea.set({ [key]: value });
    }

    async remove(key: string): Promise<void> {
        await this.storageArea.remove(key);
    }

    async clear(): Promise<void> {
        await this.storageArea.clear();
    }
}
