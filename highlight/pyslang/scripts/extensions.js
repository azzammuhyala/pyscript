// im new for this,..

// package.json
/*
    "main": "scripts/extensions.js",
    "activationEvents": ["onCommand:myext.hello"],
    "contributes": {
        "commands": [
            {
                "command": "myext.hello",
                "title": "Say Hello"
            }
        ]
    }
*/

const vscode = require('vscode');

export function activate(context) {
    console.log('Extension activate');

    const disposable = vscode.commands.registerCommand('myext.hello', () => {
        vscode.window.showInformationMessage('Hello!');
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {

}