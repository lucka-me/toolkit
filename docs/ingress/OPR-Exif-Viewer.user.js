// ==UserScript==
// @name         Wayfarer Exif Viewer
// @namespace    http://lucka.moe/
// @version      0.2.8
// @author       lucka-me
// @homepageURL  https://github.com/lucka-me/toolkit/tree/master/Ingress/OPR-Exif-Viewer
// @updateURL    https://lucka.moe/toolkit/ingress/OPR-Exif-Viewer.user.js
// @downloadURL  https://lucka.moe/toolkit/ingress/OPR-Exif-Viewer.user.js
// @match        https://wayfarer.nianticlabs.com/review*
// @grant        none
// @require      https://cdn.jsdelivr.net/npm/exif-js
// ==/UserScript==

const exifViewer = {

    // Preferences BELOW
    preferences: {
        autoRun: false, // Set to true if you want to get exif automatically when the page is loaded
        circles: [
            { radius: 45,  color: '#F00'},
            { radius: 100, color: '#00F' },
        ],  // Display circles on the map
    },
    // Preferences ABOVE

    geoKit: {
        dmsToDeg: (dms) => {
            const d = dms[0];
            const m = dms[1];
            const s = dms[2];
            return Math.round((d / 1 + m / 60 + s / 3600) * 1E6) / 1E6;
        },
        getDistance: (p1Lat, p1Lng, p2Lat, p2Lng) => {
            // Ref: https://stackoverflow.com/a/1502821/10276204
            const dLat = (p2Lat - p1Lat) * Math.PI / 180;
            const dLng = (p2Lng - p1Lng) * Math.PI / 180;
            const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(p1Lat * Math.PI / 180) * Math.cos(p2Lat * Math.PI / 180) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
            return 6378137 * c;
        },
        convertToWGS84: (fromLat, fromLng) => {
            // Ref: https://github.com/googollee/eviltransform/blob/master/javascript/transform.js
            const transform = (x, y) => {
                const xy = x * y;
                const absX = Math.sqrt(Math.abs(x));
                const xPi = x * Math.PI;
                const yPi = y * Math.PI;
                const d = 20.0 * Math.sin(6.0 * xPi) + 20.0 * Math.sin(2.0 * xPi);
                let lat = d;
                let lng = d;
                lat += 20.0 * Math.sin(yPi) + 40.0 * Math.sin(yPi / 3.0);
                lng += 20.0 * Math.sin(xPi) + 40.0 * Math.sin(xPi / 3.0);
                lat += 160.0 * Math.sin(yPi / 12.0) + 320 * Math.sin(yPi / 30.0);
                lng += 150.0 * Math.sin(xPi / 12.0) + 300.0 * Math.sin(xPi / 30.0);
                lat *= 2.0 / 3.0;
                lng *= 2.0 / 3.0;
                lat += -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * xy + 0.2 * absX;
                lng += 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * xy + 0.1 * absX;
                return { lat: lat, lng: lng };
            };
            const delta = (lat, lng) => {
                const ee = 0.00669342162296594323;
                const d = transform(lng - 105.0, lat - 35.0);
                const radLat = lat / 180.0 * Math.PI;
                const magic = Math.sin(radLat);
                const sqrtMagic = Math.sqrt(1 - ee * magic * magic);
                d.lat = (d.lat * 180.0) / ((6378137 * (1 - ee)) / (magic * sqrtMagic) * Math.PI);
                d.lng = (d.lng * 180.0) / (6378137 / sqrtMagic * Math.cos(radLat) * Math.PI);
                return d;
            };
            const d = delta(fromLat, fromLng);
            return { lat: fromLat - d.lat, lng: fromLng - d.lng };
        },
    },

    ui: {
        div: { exifResult: null, coordinateResult: null, },
        button: {
            check: {
                main: {
                    all: null, location: null,
                    disable: () => {
                        const button = exifViewer.ui.button;
                        button.disable(button.check.main.all);
                        button.check.main.all.innerHTML = 'Loading Image';
                        button.disable(button.check.main.location);
                        button.check.main.location.innerHTML = 'Loading Image';
                    },
                    enable: () => {
                        const button = exifViewer.ui.button;
                        button.enable(button.check.main.all);
                        button.check.main.all.innerHTML = 'All';
                        button.enable(button.check.main.location);
                        button.check.main.location.innerHTML = 'Location';
                    },
                },
                supporting: {
                    all: null, location: null,
                    disable: () => {
                        const button = exifViewer.ui.button;
                        button.disable(button.check.supporting.all);
                        button.check.supporting.all.innerHTML = 'Loading Image';
                        button.disable(button.check.supporting.location);
                        button.check.supporting.location.innerHTML = 'Loading Image';
                    },
                    enable: () => {
                        const button = exifViewer.ui.button;
                        button.enable(button.check.supporting.all);
                        button.check.supporting.all.innerHTML = 'All (Supporting)';
                        button.enable(button.check.supporting.location);
                        button.check.supporting.location.innerHTML = 'Location (Supporting)';
                    },
                },
            },
            convert: { portal: null, main: null, supporting: null, },
            disable: (button) => button.disabled = true ,
            enable:  (button) => button.disabled = false,
            generate: (text) => {
                const result = document.createElement('button');
                result.className = 'button-secondary';
                result.style.margin = '0.3em';
                result.innerHTML = text;
                return result;
            },
        },
        map: {
            showMarker: function(location, label, title) {
                new google.maps.Marker({
                    position: location,
                    map: exifViewer.process.subCtrl.map2,
                    label: label,
                    title: title
                });
                exifViewer.process.subCtrl.map2.panTo(location);
            },
        },
    },

    data: {
        main: null, supporting: null,
        parseLocation: (targetTags) => {
            return {
                lat: (targetTags.GPSLatitudeRef  == "N" ? 1 : -1) * exifViewer.geoKit.dmsToDeg(targetTags.GPSLatitude ),
                lng: (targetTags.GPSLongitudeRef == "E" ? 1 : -1) * exifViewer.geoKit.dmsToDeg(targetTags.GPSLongitude)
            };
        },
    },

    process: {
        subCtrl: null,
        _intervalCode: null,
        tryInit: () => { exifViewer.process._intervalCode = setInterval(exifViewer.process.init, 500); },
        init: () => {
            const process = exifViewer.process;

            if (process.subCtrl) return;
            const detect = angular.element(document.getElementById('NewSubmissionController')).scope().subCtrl;
            if (!detect.pageData) return;
            clearInterval(this._intervalCode);
            process.subCtrl = detect;

            const exifCard = document.createElement('div');
            exifCard.id = 'exif-card';
            exifCard.className = 'card card--expand';
            const cardTitle = document.createElement('div');
            cardTitle.className = 'card__header card-header';
            const cardTitleContent = document.createElement('div');
            const cardTitleHeader = document.createElement('h4');
            cardTitleHeader.className = 'card-header__title';
            cardTitleHeader.innerHTML = 'EXIF';
            cardTitleContent.appendChild(cardTitleHeader);
            cardTitle.appendChild(cardTitleContent);
            exifCard.appendChild(cardTitleContent);

            const cardBody = document.createElement('div');
            cardBody.className = 'card__body';
            const cardBodyContent = document.createElement('div');
            cardBodyContent.className = 'flexbox-grow supporting-central-field';

            const ui = exifViewer.ui;

            ui.button.check.main.all = ui.button.generate('All');
            ui.button.check.main.all.addEventListener('click', process.check.main.all);
            cardBodyContent.appendChild(ui.button.check.main.all);

            ui.button.check.main.location = ui.button.generate('Location');
            ui.button.check.main.location.addEventListener('click', process.check.main.location);
            cardBodyContent.appendChild(ui.button.check.main.location);

            if (process.subCtrl.pageData.supportingImageUrl) {
                ui.button.check.supporting.all = ui.button.generate('All (Supporting)');
                ui.button.check.supporting.all.addEventListener('click', process.check.supporting.all);
                cardBodyContent.appendChild(ui.button.check.supporting.all);

                ui.button.check.supporting.location = ui.button.generate('Location (Supporting)');
                ui.button.check.supporting.location.addEventListener('click', process.check.supporting.location);
                cardBodyContent.appendChild(ui.button.check.supporting.location);
            }

            ui.div.exifResult = document.createElement('div');
            cardBodyContent.appendChild(ui.div.exifResult);
            
            const coordConvertTitle = document.createElement('p');
            coordConvertTitle.innerHTML = 'Coordinate Conversion';
            cardBodyContent.appendChild(coordConvertTitle);

            ui.button.convert.portal = ui.button.generate('Portal');
            ui.button.convert.portal.addEventListener('click', process.convert.portal);
            cardBodyContent.appendChild(ui.button.convert.portal);

            ui.button.convert.main = ui.button.generate('Exif');
            ui.button.convert.main.addEventListener('click', process.convert.main);
            ui.button.convert.main.disabled = true;
            cardBodyContent.appendChild(ui.button.convert.main);

            if (process.subCtrl.pageData.supportingImageUrl) {
                ui.button.convert.supporting = ui.button.generate('Exif (Supporting)');
                ui.button.convert.supporting.addEventListener('click', process.convert.supporting);
                ui.button.convert.supporting.disabled = true;
                cardBodyContent.appendChild(ui.button.convert.supporting);
            }

            ui.div.coordinateResult = document.createElement('div');
            cardBodyContent.appendChild(ui.div.coordinateResult);

            exifCard.appendChild(cardBodyContent);

            const supportingCard = document.querySelector('#supporting-card');
            supportingCard.parentNode.insertBefore(exifCard, supportingCard.nextSibling);

            for (const circleOption of exifViewer.preferences.circles) {
                new google.maps.Circle({
                    strokeColor: circleOption.color,
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                    fillColor: circleOption.color,
                    fillOpacity: 0.2,
                    map: process.subCtrl.map2,
                    center: { lat: process.subCtrl.pageData.lat, lng: process.subCtrl.pageData.lng },
                    radius: circleOption.radius
                });
            }
    
            if (exifViewer.preferences.autoRun) process.check.main.location();
        },
        check: {
            main: {
                all: () => { exifViewer.process.check.all("main", exifViewer.process.subCtrl.pageData.imageUrl); },
                location: () => { exifViewer.process.check.location("main", exifViewer.process.subCtrl.pageData.imageUrl, { label: "E", title: "Exif Location" }); },
            },
            supporting: {
                all: () => { exifViewer.process.check.all("supporting", exifViewer.process.subCtrl.pageData.supportingImageUrl); },
                location: () => { exifViewer.process.check.location("supporting", exifViewer.process.subCtrl.pageData.supportingImageUrl, { label: "SE", title: "Supporting Exif Location" }); },
            },
            getTags: (type, url, onReady) => {
                const tempImg = document.createElement('img');
                tempImg.style.visibility = "hidden";
                tempImg.onload = () => {
                    const ui = exifViewer.ui;
                    if (ui.div.exifResult.childNodes.length > 0) ui.div.exifResult.appendChild(document.createElement('br'));
                    ui.div.exifResult.appendChild(document.createTextNode(`Photo size: ${tempImg.naturalWidth} × ${tempImg.naturalHeight}`));
                    EXIF.getData(tempImg, () => {
                        ui.button.check[type].enable();
                        exifViewer.data[type] = EXIF.getAllTags(this);
                        onReady();
                    });
                };
                tempImg.onerror = () => {
                    alert("Failed to load full-size photo. Maybe network error or access denied by Niantic.");
                };
                tempImg.src = url.replace("http:", "https:") + "=s0";
            },
            all: (type, imageUrl) => {
                const displayAll = () => { alert(JSON.stringify(exifViewer.data[type], null, "\t")); };
                if (exifViewer.data[type]) {
                    displayAll();
                    return;
                }
                exifViewer.ui.button.check[type].disable();
                exifViewer.process.check.getTags(type, imageUrl, displayAll);
            },
            location: (type, imageUrl, markerString) => {
                const ui = exifViewer.ui;
                const displayInfo = () => {
                    ui.button.disable(ui.button.check[type].location);
                    if (exifViewer.data[type].GPSLatitude && exifViewer.data[type].GPSLongitude) {
                        const location = data.parseLocation(data[type]);
                        ui.div.exifResult.appendChild(document.createElement('br'));
                        ui.div.exifResult.appendChild(document.createTextNode(`Distance: ${exifViewer.geoKit.getDistance(exifViewer.process.subCtrl.pageData.lat, exifViewer.process.subCtrl.pageData.lng, location.lat, location.lng).toFixed(2)} m`));
                        const buttonShowMarker = document.createElement('span');
                        buttonShowMarker.className = 'clickable ingress-mid-blue';
                        buttonShowMarker.innerHTML = '[Marker]';
                        buttonShowMarker.addEventListener('click', () => { ui.map.showMarker(location, markerString.label, markerString.title); });
                        ui.div.exifResult.appendChild(buttonShowMarker);
                        ui.div.coordinateResult.innerHTML = '';
                        ui.button.enable(ui.button.convert.portal);
                        ui.button.convert.portal.innerHTML = 'Portal';
                        ui.button.enable(ui.button.convert[type]);
                        ui.button.check[type].location.innerHTML = 'Location Checked';
                    } else {
                        ui.button.check[type].location.innerHTML = 'No Location Data';
                    }
                };
                if (exifViewer.data[type]) {
                    displayInfo();
                    return;
                }
                ui.button.check[type].disable();
                exifViewer.process.check.getTags(type, imageUrl, displayInfo);
            }
        },
        convert: {
            portal: () => {
                const ui = exifViewer.ui;
                const convertedPortalLocation = exifViewer.geoKit.convertToWGS84(exifViewer.process.subCtrl.pageData.lat, exifViewer.process.subCtrl.pageData.lng);
                ui.button.disable(ui.button.convert.portal);
                ui.button.convert.portal.innerHTML = 'Converted';
                if (ui.div.coordinateResult.childNodes.length > 0) ui.div.coordinateResult.appendChild(document.createElement('br'));
                if (exifViewer.data.main && exifViewer.data.main.GPSLatitude) {
                    const exifLocation = exifViewer.data.parseLocation(exifViewer.data.main);
                    ui.div.coordinateResult.appendChild(document.createTextNode(`Converted Portal ↔︎ Original Exif: ${exifViewer.geoKit.getDistance(convertedPortalLocation.lat, convertedPortalLocation.lng, exifLocation.lat, exifLocation.lng).toFixed(2)} m`));
                } else {
                    ui.div.coordinateResult.appendChild(document.createTextNode("Converted Portal: "));
                }
                const buttonShowMarker = document.createElement('span');
                buttonShowMarker.className = 'clickable ingress-mid-blue';
                buttonShowMarker.innerHTML = '[Marker]';
                buttonShowMarker.addEventListener('click', () => { ui.map.showMarker(convertedPortalLocation, "CP", "Converted Portal Location"); });
                ui.div.coordinateResult.appendChild(buttonShowMarker);
            },
            main: () => { exifViewer.process.convert.exif("main", { prefix: "Converted", markerLabel: "CE" }); },
            supporting: () => { exifViewer.process.convert.exif("supporting", { prefix: "Converted Supporting", markerLabel: "CSE" }); },
            exif: (type, strings) => {
                const ui = exifViewer.ui;
                const exifLocation = exifViewer.data.parseLocation(exifViewer.data[type]);
                const convertedExifLocation = exifViewer.geoKit.convertToWGS84(exifLocation.lat, exifLocation.lng);
                ui.button.disable(ui.button.convert[type]);
                ui.button.convert[type].innerHTML = 'Converted';
                if (ui.div.coordinateResult.childNodes.length > 0) ui.div.coordinateResult.appendChild(document.createElement('br'));
                ui.div.coordinateResult.appendChild(document.createTextNode(`${strings.prefix} Exif ↔︎ Original Portal: ${exifViewer.geoKit.getDistance(exifViewer.process.subCtrl.pageData.lat, exifViewer.process.subCtrl.pageData.lng, convertedExifLocation.lat, convertedExifLocation.lng).toFixed(2)} m`));
                const buttonShowMarker = document.createElement('span');
                buttonShowMarker.className = 'clickable ingress-mid-blue';
                buttonShowMarker.innerHTML = '[Marker]';
                buttonShowMarker.addEventListener('click', () => { ui.map.showMarker(convertedExifLocation, strings.markerLabel, strings.prefix + " Exif Location"); });
                ui.div.coordinateResult.appendChild(buttonShowMarker);
            },
        },
    },
};

exifViewer.process.tryInit();