const path = require('path');
const fs = require('fs');
const CopyPlugin = require('copy-webpack-plugin');
const webpack = require('webpack');
const ZipPlugin = require('zip-webpack-plugin');
const srcDir = path.resolve(__dirname, '..', 'src');
const packageJson = require('./../package.json');

function generateEntryObj(srcPath) {
    const entries = {};

    fs.readdirSync(srcPath).forEach((file) => {
        if (file.endsWith('.ts')) {
            const basename = path.basename(file, '.ts');
            entries[basename] = path.join(srcPath, file);
        }
    });

    return entries;
}

function createCopyPlugin(patterns, replacements = {}) {
    return new CopyPlugin({
        patterns: patterns.map((pattern) => {
            if (Object.keys(replacements).length > 0 && pattern.transform) {
                return {
                    ...pattern,
                    transform(content) {
                        let transformedContent = content.toString();
                        for (const [placeholder, value] of Object.entries(replacements)) {
                            transformedContent = transformedContent.replace(new RegExp(placeholder, 'g'), value);
                        }
                        return transformedContent;
                    },
                };
            }
            return pattern;
        }),
    });
}

const common = {
    mode: 'production',
    entry: generateEntryObj(srcDir),
    resolve: {
        extensions: ['.ts', '.js'],
    },
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                loader: 'ts-loader',
                exclude: /node_modules/,
            },
        ],
    },
    plugins: [
        new webpack.ProvidePlugin({
            browser: 'webextension-polyfill',
        }),
    ],
};

const outputPath = (subfolder) => path.join(__dirname, '..', 'dist', subfolder);
const outputFilename = '[name].js';
const replacements = {
    '%VERSION%': packageJson.version,
    '%NAME%': packageJson.extensionName,
    '%DESCRIPTION%': packageJson.description,
};

const zipFilename = (browser) => {
    const version = packageJson.version.replace(/\./g, '-');
    return `${browser}_${version}.zip`;
};

module.exports = [
    ['chrome', 'manifest.chrome.json'],
    ['firefox', 'manifest.firefox.json'],
].map(([target, manifestFile]) => ({
    ...common,
    output: {
        path: outputPath(target),
        filename: outputFilename,
    },
    plugins: [
        ...common.plugins,
        createCopyPlugin(
            [
                {
                    from: `public/${manifestFile}`,
                    to: 'manifest.json',
                    transform: true
                },
                {
                    from: 'public',
                    to: '.',
                    globOptions: {
                        ignore: ['**/manifest.chrome.json', '**/manifest.firefox.json'],
                    },
                    noErrorOnMissing: true,
                },
                {
                    from: srcDir,
                    to: '.',
                    globOptions: {
                        ignore: ['**/*.ts'],
                    },
                    noErrorOnMissing: true,
                },
            ].filter(Boolean),
            replacements,
        ),
        new ZipPlugin({
            path: path.join(__dirname, '..', 'dist'),
            filename: zipFilename(target),
            pathMapper: (assetPath) => {
                return assetPath;
            },
        }),
    ],
}));
