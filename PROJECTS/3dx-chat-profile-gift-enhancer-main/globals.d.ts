import * as browserNamespace from 'webextension-polyfill';

declare global {
    const browser: typeof browserNamespace;
}
