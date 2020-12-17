// ==UserScript==
// @name         Beldum
// @namespace    http://lucka.moe/
// @version      0.1.0
// @description  Automatically replace and process when edit page
// @author       Lucka
// @match        https://wiki.52poke.com/*
// @grant        none
// ==/UserScript==

const Beldum = {
    data: {
        title: /.+/,
        replaceList: [
            [ /<br>/g, '<br/>' ],
        ],
        procList: [
            (code) => {
                const heading = document.querySelector('h1#firstHeading').innerHTML;
                return `-{T|${heading.toLocaleUpperCase()}}-\n\n${code}`;
            },
        ],
        minorEdit: true,
        summary: '/* <br> -> <br/> */',
    },
    exec() {
        // Find editor
        const editor = document.querySelector('#wpTextbox1');
        if (!editor) return;
        // Match title
        if (document.querySelector('h1#firstHeading').innerHTML.search(this.data.title) < 0) return;
        // Save code
        let code = editor.value;
        // Replace
        for (const replace of this.data.replaceList) {
            code = code.replace(replace[0], replace[1]);
        }
        // Processes
        for (const proc of this.data.procList) code = proc(code);
        // Update code
        editor.value = code;
        // Minor edit
        document.querySelector('#wpMinoredit').checked = this.data.minorEdit;
        // Summary
        window.setTimeout(() => {
            document.querySelector('#wpSummary').value = this.data.summary;
        }, 500);
    },
};

Beldum.exec();