# Dark Mode CSS for Niantic Wayfarer
Enable dark mode for [Niantic Wayfarer](https://wayfarer.nianticlabs.com/).

[![Userscript version](https://img.shields.io/badge/css-v0.1.13-green)](https://lucka.moe/toolkit/ingress/wayfarer-dark.css) [![Userscript version](https://img.shields.io/badge/userscript-v0.1.3-green)](https://lucka.moe/toolkit/ingress/Wayfarer-Dark-Mode.user.js)

## Usage
Load [this CSS](https://lucka.moe/toolkit/ingress/wayfarer-dark.css) with:
1. A simple userscript: [Install](https://lucka.moe/toolkit/ingress/Wayfarer-Dark-Mode.user.js)
2. Userstyles manager like [Stylus](https://github.com/openstyles/stylus "Github")

### Enable automatically switch
Check compability of your browser [here](https://developer.mozilla.org/docs/Web/CSS/@media/prefers-color-scheme "MDN"), the latest Chrome, Firefox and Safari support dark mode.

If you use CSS with: 
1. The userscript (not real-time, must refresh the page):  
   Uncomment the code:
    ```javascript
    if (!window.matchMedia('(prefers-color-scheme: dark)').matches) return;
    ```
2. Userstyles manager (real-time):  
   Put all other rules in this one:
   ```css
   @media (prefers-color-scheme: dark) { }
   ```

## References
- [Dark Mode in CSS | CSS-Tricks](https://css-tricks.com/dark-modes-with-css/)  
  How to enable dark mode with `prefers-color-scheme`
- [Dark Theme - Material Design](https://material.io/design/color/dark-theme.html)

## Changelog

### [0.1.13] - 2020-10-22
#### Changed
- Support new stars style


<details><summary>Previous</summary>
<p>

### [0.1.12] - 2020-03-25
#### Changed
- Color of selected category

#### Fixed
- Color of back arrow in catrgory selector card


### [0.1.11] - 2020-03-24
#### Changed
- Support category selector (.suggestions-check label)


### [0.1.10] - 2019-11-14
#### Changed
- Support background color for .container


### [0.1.9] - 2019-11-10
#### Fixed
- Bold text color in Help pages


### [0.1.8] - 2019-10-26
#### Changed
- Update for category selector
- Update for known-infomation card


### [0.1.7] - 2019-10-26
#### Fixed
- Title background in sub-page of settings
- Dropdown css in settings


### [0.1.6] - 2019-10-16
#### Changed
- Text color

#### Fixed
- Edit: Known information
- Cancel button in dialog
- .ingress-mid-blue


### [0.1.5] - 2019-10-15
#### Fixed
- Cookiebar


### [0.1.4] - 2019-10-14
#### Fixed
- Nomination upgrade dialog background
- Nomination upgrade button color


### [0.1.3] - 2019-10-13
#### Changed
- Support the entire Wayfarer
- Force to enter dark mode for default


### [0.1.2] - 2019-10-13
#### Changed
- Run script as fast as possible, set a loop if the document.head doesn't exist


### [0.1.1] - 2019-10-13
#### Changed
- CSS improved
- Run script when body exists


### [0.1.0] - 2019-10-13
Initial version
```

</p>
</details>