import { extensions, highlightRules } from './highlight';
import { snippets } from './snippets';
import plugin from '../plugin.json';

const url = acode.require('url');
const aceModes = acode.require('aceModes');
const snippetManager = ace.require('ace/snippets').snippetManager;

class PyScriptPlugin {

    async init(baseUrl, $page, options) {
        $page.id = plugin.id;

        // highlight

        ace.define('ace/mode/pyscript', function (require, exports, module) {
            const oop = require('ace/lib/oop');
            const TextMode = require('ace/mode/text').Mode;
            const TextHighlightRules = require('ace/mode/text_highlight_rules').TextHighlightRules;

            // means:
            // class HighlightRules extends TextHighlightRules {
            //     constructor() {
            //         this.$rules = highlightRules;
            //         this.normalizeRules();
            //     }
            // }
            const HighlightRules = function () {
                this.$rules = highlightRules;
                this.normalizeRules();
            };
            oop.inherits(HighlightRules, TextHighlightRules);

            // means:
            // class Mode extends TextMode {
            //     constructor() {
            //         super();
            //         this.HighlightRules = HighlightRules;
            //         ...
            //     }
            // }
            const Mode = function () {
                TextMode.call(this);
                this.HighlightRules = HighlightRules;

                // performs additional special parsing for single strings
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
                    if (singleStringStates.includes(result.state) && !line.endsWith('\\')) {
                        result.state = 'start';
                    }
                    return result;
                };
            };
            oop.inherits(Mode, TextMode);

            exports.Mode = Mode;
        });

        aceModes.addMode('pyscript', extensions, 'PyScript');

        // icon

        const iconPath = baseUrl + 'PyScript.png';
        acode.addIcon('pyscript-icon', iconPath);
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

        // snippet

        this.snippet = snippetManager.parseSnippetFile(snippets);
        snippetManager.register(this.snippet, 'pyscript');
        editorManager.editor.setOptions({
            enableBasicAutocompletion: true,
            enableSnippets: true,
            enableLiveAutocompletion: true
        });

        this.updateSession('pyscript');
    }

    async destroy() {
        this.iconStyle.remove();
        snippetManager.unregister(this.snippet, 'pyscript');
        this.updateSession('text');
        aceModes.removeMode('pyscript');
    }

    applyPluginToFile(file) {
        if (url.extname(file.name) === '.pys') {
            file.session.setMode(`ace/mode/pyscript`);
        }
    }

    updateSession(mode) {
        for (const file of editorManager.files) {
            if (!file || !file.name) {
                continue
            }
            this.applyPluginToFile(file);
        }
        editorManager.emit('update');
    }

}

const waitForAcodeReady = async () => {
    while (
        !window.acode ||
        !window.acode.setPluginInit ||
        !window.editorManager ||
        !window.acode.require ||
        document.readyState === 'loading'
    ) {
        await new Promise((resolve) => setTimeout(resolve, 250));
    }
};

if (window.acode) {
    waitForAcodeReady().then(() => {
        const pyScriptPlugin = new PyScriptPlugin();

        acode.setPluginInit(plugin.id, async (baseUrl, $page, options) => {
            await pyScriptPlugin.init(
                baseUrl.endsWith('/') ? baseUrl : baseUrl + '/',
                $page,
                options
            );
        });

        acode.setPluginUnmount(plugin.id, () => {
            pyScriptPlugin.destroy();
        });
    });
}