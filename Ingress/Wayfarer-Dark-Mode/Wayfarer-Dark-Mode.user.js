// ==UserScript==
// @name         Wayfarer Dark Mode
// @namespace    http://lucka.moe/
// @version      0.1.3
// @author       lucka-me
// @homepageURL  https://github.com/lucka-me/toolkit/tree/master/Ingress/Wayfarer-Dark-Mode
// @updateURL    https://lucka.moe/toolkit/ingress/Wayfarer-Dark-Mode.user.js
// @downloadURL  https://lucka.moe/toolkit/ingress/Wayfarer-Dark-Mode.user.js
// @match        https://wayfarer.nianticlabs.com/*
// @run-at       document-start
// ==/UserScript==

const enableDarkMode = () => {

    // Uncomment the code below if you want to follow the browser / system color
    // mode automatically when load the page
    // Notice: MUST refresh the page after switching the browser / system color
    // mode, NOT real-time
    //if (!window.matchMedia('(prefers-color-scheme: dark)').matches) return;

    const link = document.createElement('link');
    link.type = 'text/css';
    link.rel = 'stylesheet';
    link.href = 'https://lucka.moe/toolkit/ingress/wayfarer-dark.css';

    let intervalCode = null;
    const loadCSS = () => {
        if (document.head) {
            if (intervalCode) clearInterval(intervalCode);
            document.head.appendChild(link);
        }
    };
    if (document.head) {
        loadCSS();
    } else {
        intervalCode = setInterval(loadCSS, 100);
    }
};

enableDarkMode();