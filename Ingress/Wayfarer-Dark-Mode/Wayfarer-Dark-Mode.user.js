// ==UserScript==
// @name         Wayfarer Dark Mode
// @namespace    http://lucka.moe/
// @version      0.1.1
// @author       lucka-me
// @homepageURL  https://github.com/lucka-me/toolkit/tree/master/Ingress/Wayfarer-Dark-Mode
// @updateURL    https://lucka.moe/toolkit/ingress/Wayfarer-Dark-Mode.user.js
// @downloadURL  https://lucka.moe/toolkit/ingress/Wayfarer-Dark-Mode.user.js
// @match        https://wayfarer.nianticlabs.com/review*
// @run-at       document-body
// ==/UserScript==

const enableDarkMode = () => {
    const link = document.createElement('link');
    link.type = 'text/css';
    link.rel = 'stylesheet';
    link.href = 'https://lucka.moe/toolkit/ingress/wayfarer-dark.css';
    document.head.appendChild(link);
};

enableDarkMode();