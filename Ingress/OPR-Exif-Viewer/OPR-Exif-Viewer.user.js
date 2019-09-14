// ==UserScript==
// @name         OPR Exif Viewer
// @namespace    http://lucka.moe/
// @version      0.2.7
// @author       lucka-me
// @homepageURL  https://github.com/lucka-me/toolkit/tree/master/Ingress/OPR-Exif-Viewer
// @updateURL    https://lucka.moe/toolkit/ingress/OPR-Exif-Viewer.user.js
// @downloadURL  https://lucka.moe/toolkit/ingress/OPR-Exif-Viewer.user.js
// @match        https://opr.ingress.com/recon
// @grant        none
// @require      https://code.jquery.com/jquery-3.3.1.min.js
// @require      https://cdn.jsdelivr.net/npm/exif-js
// ==/UserScript==

const exifViewer = {

    // Preferences BELOW
    preferences: {
        autoRun: false, // Set to true if you want to get exif automatically when the page is loaded
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
                        button.check.main.all.html("Loading Image");
                        button.disable(button.check.main.location);
                        button.check.main.location.html("Loading Image");
                    },
                    enable: () => {
                        const button = exifViewer.ui.button;
                        button.enable(button.check.main.all);
                        button.check.main.all.html("All");
                        button.enable(button.check.main.location);
                        button.check.main.location.html("Location");
                    },
                },
                supporting: {
                    all: null, location: null,
                    disable: () => {
                        const button = exifViewer.ui.button;
                        button.disable(button.check.supporting.all);
                        button.check.supporting.all.html("Loading Image");
                        button.disable(button.check.supporting.location);
                        button.check.supporting.location.html("Loading Image");
                    },
                    enable: () => {
                        const button = exifViewer.ui.button;
                        button.enable(button.check.supporting.all);
                        button.check.supporting.all.html("All (Supporting)");
                        button.enable(button.check.supporting.location);
                        button.check.supporting.location.html("Location (Supporting)");
                    },
                },
            },
            convert: { portal: null, main: null, supporting: null, },
            disable: (button) => { button.prop("disabled", true ); },
            enable:  (button) => { button.prop("disabled", false); },
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
                lat: (targetTags.GPSLatitudeRef  == "N" ? 1 : -1) * geoKit.dmsToDeg(targetTags.GPSLatitude ),
                lng: (targetTags.GPSLongitudeRef == "E" ? 1 : -1) * geoKit.dmsToDeg(targetTags.GPSLongitude)
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
    
            const descDiv = $('#descriptionDiv');
            descDiv.append('<br/><small class="gold">EXIF</small><br/>');
            const exifDiv = $('<div></div>');
            descDiv.append(exifDiv);

            const ui = exifViewer.ui;
    
            ui.button.check.main.all = $('<button type="button" class="button">All</button>');
            ui.button.check.main.all.click(process.check.main.all);
            exifDiv.append(ui.button.check.main.all);
    
            ui.button.check.main.location = $('<button type="button" class="button">Location</button>');
            ui.button.check.main.location.click(process.check.main.location);
            exifDiv.append(ui.button.check.main.location);
    
            if (process.subCtrl.pageData.supportingImageUrl) {
                ui.button.check.supporting.all = $('<button type="button" class="button">All (Supporting)</button>');
                ui.button.check.supporting.all.click(process.check.supporting.all);
                exifDiv.append(ui.button.check.supporting.all);
    
                ui.button.check.supporting.location = $('<button type="button" class="button">Location (Supporting)</button>');
                ui.button.check.supporting.location.click(process.check.supporting.location);
                exifDiv.append(ui.button.check.supporting.location);
            }
    
            ui.div.exifResult = $('<div></div>');
            exifDiv.append(ui.div.exifResult);
            exifDiv.append("<small class=\"gold\">Coordinate Conversion</small><br/>");
    
            ui.button.convert.portal = $('<button type="button" class="button">Portal</button>');
            ui.button.convert.portal.click(process.convert.portal);
            exifDiv.append(ui.button.convert.portal);
    
            ui.button.convert.main = $('<button type="button" class="button" disabled="true">Exif</button>');
            ui.button.convert.main.click(process.convert.main);
            exifDiv.append(ui.button.convert.main);
    
            if (process.subCtrl.pageData.supportingImageUrl) {
                ui.button.convert.supporting = $('<button type="button" class="button" disabled="true">Exif (Supporting)</button>');
                ui.button.convert.supporting.click(process.convert.supporting);
                exifDiv.append(ui.button.convert.supporting);
            }
    
            ui.div.coordinateResult = $('<div></div>');
            exifDiv.append(ui.div.coordinateResult);

            new google.maps.Circle({
                strokeColor: "#00F",
                strokeOpacity: 0.8,
                strokeWeight: 2,
                fillColor: "#00F",
                fillOpacity: 0.2,
                map: process.subCtrl.map2,
                center: { lat: process.subCtrl.pageData.lat, lng: process.subCtrl.pageData.lng },
                radius: 100
            });

            new google.maps.Circle({
                strokeColor: "#F00",
                strokeOpacity: 0.8,
                strokeWeight: 2,
                fillColor: "#F00",
                fillOpacity: 0.2,
                map: process.subCtrl.map2,
                center: { lat: process.subCtrl.pageData.lat, lng: process.subCtrl.pageData.lng },
                radius: 40
            });
    
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
                    if ($.trim(ui.div.exifResult.html())) ui.div.exifResult.append("<br/>");
                    ui.div.exifResult.append(`Photo size: ${tempImg.naturalWidth} × ${tempImg.naturalHeight}`);
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
                        ui.div.exifResult.append(
                            "<br/>Distance: " + exifViewer.geoKit.getDistance(exifViewer.process.subCtrl.pageData.lat, exifViewer.process.subCtrl.pageData.lng, location.lat, location.lng).toFixed(2) + "m "
                        );
                        const buttonShowMarker = $('<span class="clickable ingress-mid-blue">[Marker]</span>');
                        buttonShowMarker.click(() => { ui.map.showMarker(location, markerString.label, markerString.title); });
                        ui.div.exifResult.append(buttonShowMarker);
                        ui.div.coordinateResult.html("");
                        ui.button.enable(ui.button.convert.portal);
                        ui.button.convert.portal.html("Portal");
                        ui.button.enable(ui.button.convert[type]);
                        ui.button.check[type].location.html("Location Checked");
                    } else {
                        ui.button.check[type].location.html("No Location Data");
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
                ui.button.convert.portal.html("Converted");
                if ($.trim(ui.div.coordinateResult.html())) ui.div.coordinateResult.append("<br/>");
                if (exifViewer.data.main && exifViewer.data.main.GPSLatitude) {
                    const exifLocation = exifViewer.data.parseLocation(exifViewer.data.main);
                    ui.div.coordinateResult.append("Converted Portal ↔︎ Original Exif: " + exifViewer.geoKit.getDistance(convertedPortalLocation.lat, convertedPortalLocation.lng, exifLocation.lat, exifLocation.lng).toFixed(2) + "m ");
                } else {
                    ui.div.coordinateResult.append("Converted Portal: ");
                }
                const buttonShowMarker = $('<span class="clickable ingress-mid-blue">[Marker]</span>');
                buttonShowMarker.click(function() { ui.map.showMarker(convertedPortalLocation, "CP", "Converted Portal Location"); });
                ui.div.coordinateResult.append(buttonShowMarker);
            },
            main: () => { exifViewer.process.convert.exif("main", { prefix: "Converted", markerLabel: "CE" }); },
            supporting: () => { exifViewer.process.convert.exif("supporting", { prefix: "Converted Supporting", markerLabel: "CSE" }); },
            exif: (type, strings) => {
                const ui = exifViewer.ui;
                const exifLocation = exifViewer.data.parseLocation(exifViewer.data[type]);
                const convertedExifLocation = exifViewer.geoKit.convertToWGS84(exifLocation.lat, exifLocation.lng);
                ui.button.disable(ui.button.convert[type]);
                ui.button.convert[type].html("Converted");
                if ($.trim(ui.div.coordinateResult.html())) ui.div.coordinateResult.append("<br/>");
                ui.div.coordinateResult.append(strings.prefix + " Exif ↔︎ Original Portal: " + geoKit.getDistance(exifViewer.process.subCtrl.pageData.lat, exifViewer.process.subCtrl.pageData.lng, convertedExifLocation.lat, convertedExifLocation.lng).toFixed(2) + "m ")
                const buttonShowMarker = $('<span class="clickable ingress-mid-blue">[Marker]</span>');
                buttonShowMarker.click(() => { ui.map.showMarker(convertedExifLocation, strings.markerLabel, strings.prefix + " Exif Location"); });
                ui.div.coordinateResult.append(buttonShowMarker);
            },
        },
    },
};

exifViewer.process.tryInit();