const path = require('path');
const vscode = require('vscode');
const { LanguageClient } = require('vscode-languageclient/node');

let client;

function activate(context) {
    const serverOptions = {
        command: 'python3',
        args: [path.join(context.extensionPath, 'norm_ls.py')]
    };

    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'c' }]
    };

    client = new LanguageClient(
        'norm_ls',
        'Norminette in a language server',
        serverOptions,
        clientOptions
    );

    client.start();
}

function deactivate() {
    if (!client) {
        return undefined;
    }
    return client.stop();
}

module.exports = {
    activate,
    deactivate
};