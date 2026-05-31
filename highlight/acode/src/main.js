import { extensions, highlightRules } from './highlight';
import { snippets } from './snippets';
import plugin from '../plugin.json';

class PyScriptPlugin {

    async init(baseUrl, $page, options) {
        $page.id = plugin.id;

        // Icon

        const iconPath = baseUrl + 'PyScript.png';

        // This method works, but not when the Acode app is first run on a previously opened file.
        // The file needs to be reopened.
        this.iconStyle = document.createElement('style');
        this.iconStyle.textContent = `
        .file_type_pyscript::before {
            display: inline-block;
            content: '';
            background-image: url(${iconPath});
            background-size: contain;
            background-repeat: no-repeat;
            height: 1em;
            width: 1em;
        }`;
        document.head.append(this.iconStyle);

        // Highlight

        ace.define('ace/mode/pyscript', function (require, exports, module) {
            const TextMode = require('ace/mode/text').Mode;
            const TextHighlightRules = require('ace/mode/text_highlight_rules').TextHighlightRules;

            class HighlightRules extends TextHighlightRules {
                constructor() {
                    super();
                    this.$rules = highlightRules;
                    this.normalizeRules();
                }
            }

            class Mode extends TextMode {
                constructor() {
                    super();
                    this.HighlightRules = HighlightRules;

                    // Performs additional special parsing for single strings
                    /*
                        PROBLEM:
                            When a prefix string (" or ') encounters an EOL instead of at least one other character, the
                            next line is included in the string that should terminate at the EOL (except for multiline
                            continuation). This can be seen in the following illustration:

                            CODE:
                                "string
                                code

                            RESULT (pseudocode html) [Status: VALID]:
                                <string>"string</string>
                                <identifier>code</identifier>

                            =============================================

                            CODE:
                                "
                                code

                            RESULT (pseudocode html) [Status: INVALID]:
                                <string>"
                                code</string>

                            To address this, an additional script was created to handle this single string state.
                    */
                    const tokenizer = this.getTokenizer();
                    const originalGetLineTokens = tokenizer.getLineTokens.bind(tokenizer);
                    const singleStringStates = [
                        'string_apostrophe_single',
                        'string_quotation_single',
                        'raw_string_apostrophe_single',
                        'raw_string_quotation_single'
                    ];

                    tokenizer.getLineTokens = function(line, state) {
                        const result = originalGetLineTokens(line, state);
                        if (singleStringStates.includes(result.state) && !line.endsWith('\\'))
                            result.state = 'start';
                        return result;
                    };
                }
            }

            exports.Mode = Mode;
        });

        aceModes.addMode('pyscript', extensions, 'PyScript');

        // Snippet

        this.snippet = snippetManager.parseSnippetFile(snippets);
        snippetManager.register(this.snippet, 'pyscript');
        editorManager.editor.setOptions({
            enableBasicAutocompletion: true,
            enableSnippets: true,
            enableLiveAutocompletion: true
        });

        // Begin

        this.toPyscript = () => this.updateActiveFile('pyscript');
        editorManager.on('switch-file', this.toPyscript);
        editorManager.on('rename-file', this.toPyscript);
        this.updateAllFiles('pyscript');
    }

    async destroy() {
        editorManager.off('switch-file', this.toPyscript);
        editorManager.off('rename-file', this.toPyscript);
        this.iconStyle.remove();
        this.updateAllFiles('text');
        aceModes.removeMode('pyscript');
        snippetManager.unregister(this.snippet, 'pyscript');
    }

    applyPluginToFile(file, mode) {
        if (!file)
            return;

        const fileExtension = url.extname(file.name);
        if (extensions.includes(fileExtension.startsWith('.') ? fileExtension.slice(1) : fileExtension))
            file.session.setMode(`ace/mode/${mode}`);
    }

    updateActiveFile(mode) {
        this.applyPluginToFile(editorManager.activeFile, mode);
        editorManager.emit('update');
    }

    updateAllFiles(mode) {
        for (const file of editorManager.files)
            this.applyPluginToFile(file, mode);
        editorManager.emit('update');
    }

}

const waitForAcodeReady = async () => {
    while (
        !window.acode ||
        !window.ace ||
        !window.editorManager ||
        !window.acode.setPluginInit ||
        !window.acode.setPluginUnmount ||
        !window.acode.require ||
        !window.ace.require ||
        document.readyState === 'loading'
    ) await new Promise((resolve) => setTimeout(resolve, 250));
};

waitForAcodeReady().then(() => {
    window.url = acode.require('url');
    window.aceModes = acode.require('aceModes');
    window.snippetManager = ace.require('ace/snippets').snippetManager;

    const pyScriptPlugin = new PyScriptPlugin();

    acode.setPluginInit(plugin.id, async (baseUrl, $page, options) => {
        await pyScriptPlugin.init(
            baseUrl.endsWith('/') ? baseUrl : baseUrl + '/',
            $page,
            options
        );
    });

    acode.setPluginUnmount(plugin.id, async () => {
        await pyScriptPlugin.destroy();
    });
});