// ==UserScript==
// @name         OPR Exif Viewer
// @namespace    http://lucka.moe/
// @version      0.2.0
// @author       lucka-me
// @homepageURL  https://github.com/lucka-me/toolkit/tree/master/Ingress/OPR-Exif-Viewer
// @updateURL    https://lucka.moe/toolkit/ingress/OPR-Exif-Viewer.user.js
// @downloadURL  https://lucka.moe/toolkit/ingress/OPR-Exif-Viewer.user.js
// @match        https://opr.ingress.com/recon
// @grant        none
// @require      https://code.jquery.com/jquery-3.3.1.min.js
// @require      https://cdn.jsdelivr.net/npm/exif-js
// ==/UserScript==

// Preferences BELOW
const preferences = {
    autoRun: false // Set to true if you want to get exif automatically when the page is loaded
};
// Preferences ABOVE

const geoKit = {
    dmsToDeg: function(dms) {
        let d = dms[0];
        let m = dms[1];
        let s = dms[2];
        return Math.round((d / 1 + m / 60 + s / 3600) * 1E6) / 1E6;
    },
    getDistance: function(p1Lat, p1Lng, p2Lat, p2Lng) {
        // Ref: https://stackoverflow.com/a/1502821/10276204
        let dLat = (p2Lat - p1Lat) * Math.PI / 180;
        let dLng = (p2Lng - p1Lng) * Math.PI / 180;
        let a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(p1Lat * Math.PI / 180) * Math.cos(p2Lat * Math.PI / 180) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
        let c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return 6378137 * c;
    },
    convertToWGS84: function(fromLat, fromLng) {
        // Ref: https://github.com/googollee/eviltransform/blob/master/javascript/transform.js
        const transform = function(x, y) {
            let xy = x * y;
            let absX = Math.sqrt(Math.abs(x));
            let xPi = x * Math.PI;
            let yPi = y * Math.PI;
            let d = 20.0 * Math.sin(6.0 * xPi) + 20.0 * Math.sin(2.0 * xPi);
            let lat = d;
            let lng = d;
            lat += 20.0 * Math.sin(yPi) + 40.0 * Math.sin(yPi/3.0);
            lng += 20.0 * Math.sin(xPi) + 40.0 * Math.sin(xPi/3.0);
            lat += 160.0 * Math.sin(yPi/12.0) + 320 * Math.sin(yPi/30.0);
            lng += 150.0 * Math.sin(xPi/12.0) + 300.0 * Math.sin(xPi/30.0);
            lat *= 2.0 / 3.0;
            lng *= 2.0 / 3.0;
            lat += -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * xy + 0.2 * absX;
            lng += 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * xy + 0.1 * absX;
            return {lat: lat, lng: lng}
        };
        const delta = function(lat, lng) {
            const ee = 0.00669342162296594323;
            let d = transform(lng - 105.0, lat - 35.0);
            let radLat = lat / 180.0 * Math.PI;
            let magic = Math.sin(radLat);
            magic = 1 - ee * magic * magic;
            let sqrtMagic = Math.sqrt(magic);
            d.lat = (d.lat * 180.0) / ((6378137 * (1 - ee)) / (magic * sqrtMagic) * Math.PI);
            d.lng = (d.lng * 180.0) / (6378137 / sqrtMagic * Math.cos(radLat) * Math.PI);
            return d;
        };
        let d = delta(fromLat, fromLng);
        return { lat: fromLat - d.lat, lng: fromLng - d.lng };
    },
}

const ui = {
    div: {
        exifResult: null,
        coordinateResult: null,
    },
    button: {
        check: {
            main: {
                all: null,
                location: null,
                disable: function() {
                    ui.button.disable(ui.button.check.main.all);
                    ui.button.check.main.all.html("Loading Image");
                    ui.button.disable(ui.button.check.main.location);
                    ui.button.check.main.location.html("Loading Image");
                },
                enable: function() {
                    ui.button.enable(ui.button.check.main.all);
                    ui.button.check.main.all.html("All");
                    ui.button.enable(ui.button.check.main.location);
                    ui.button.check.main.location.html("Location");
                },
            },
            supporting: {
                all: null,
                location: null,
            },
        },
        convert: {
            portal: null,
            main: null,
            supporting: null,
        },
        disable: function(button) { button.prop("disabled", true); },
        enable: function(button) { button.prop("disabled", false); },
    },
    map: {
        showMarker: function(location, label, title) {
            new google.maps.Marker({
                position: location,
                map: process.subCtrl.map2,
                label: label,
                title: title
            });
            process.subCtrl.map2.panTo(location);
        },
    }
};

const tags = {
    main: null,
    supporting: null,
    parseLocation: function(targetTags) {
        return {
            lat: (targetTags.GPSLatitudeRef == "N" ? 1 : -1) * geoKit.dmsToDeg(targetTags.GPSLatitude),
            lng: (targetTags.GPSLongitudeRef == "E" ? 1 : -1) * geoKit.dmsToDeg(targetTags.GPSLongitude)
        };
    },
};

const process = {
    subCtrl: null,
    onload: function() {
        if (process.subCtrl) return;
        let detect = angular.element(document.getElementById('NewSubmissionController')).scope().subCtrl;
        if (!detect) return;
        process.subCtrl = detect;

        let descDiv = $('#descriptionDiv');
        descDiv.append('<br/><small class="gold">EXIF</small><br/>');
        let exifDiv = $('<div></div>');
        descDiv.append(exifDiv);

        ui.button.check.main.all = $('<button type="button" class="button">All</button>');
        ui.button.check.main.all.click(process.check.main.all);
        exifDiv.append(ui.button.check.main.all);

        ui.button.check.main.location = $('<button type="button" class="button">Location</button>');
        ui.button.check.main.location.click(process.check.main.location);
        exifDiv.append(ui.button.check.main.location);

        ui.div.exifResult = $('<div></div>');
        exifDiv.append(ui.div.exifResult);
        exifDiv.append("<small class=\"gold\">Coordinate Conversion</small><br/>");

        ui.button.convert.portal = $('<button type="button" class="button">Portal</button>');
        ui.button.convert.portal.click(process.convert.portal);
        exifDiv.append(ui.button.convert.portal);

        ui.button.convert.main = $('<button type="button" class="button" disabled="true">Exif</button>');
        ui.button.convert.main.click(process.convert.main);
        exifDiv.append(ui.button.convert.main);

        ui.div.coordinateResult = $('<div></div>');
        exifDiv.append(ui.div.coordinateResult);

        if (preferences.autoRun) process.check.main;
    },
    check: {
        main: {
            all: function() {
                let displayAll = function() { alert(JSON.stringify(tags.main, null, "\t")); };
                if (tags.main) {
                    displayAll();
                    return;
                }
                ui.button.check.main.disable();
                process.check.getTags(process.subCtrl.pageData.imageUrl, function(result) {
                    ui.button.check.main.enable();
                    tags.main = result;
                    displayAll();
                });
            },
            location: function() {
                let displayInfo = function() {
                    ui.button.disable(ui.button.check.main.location);
                    if (tags.main.GPSLatitude && tags.main.GPSLongitude) {
                        let location = tags.parseLocation(tags.main);
                        ui.div.exifResult.append(
                            "Distance: " + geoKit.getDistance(subCtrl.pageData.lat, subCtrl.pageData.lng, location.lat(), location.lng()).toFixed(2) + "m "
                        );
                        let buttonShowMarker = $('<span class="clickable ingress-mid-blue">[Marker]</span>');
                        buttonShowMarker.click(function() { ui.map.showMarker(location, "E", "Exif Location"); });
                        ui.div.exifResult.append(buttonShowMarker);
                        ui.div.coordinateResult.html("");
                        ui.button.enable(ui.button.convert.portal);
                        ui.button.convert.portal.html("Portal");
                        ui.button.enable(ui.button.convert.main);
                        ui.button.check.main.location.html("Location Checked");
                    } else {
                        ui.button.check.main.location.html("No Location Data");
                    }
                };
                if (tags.main) {
                    displayInfo();
                    return;
                }
                ui.button.check.main.disable();
                process.check.getTags(process.subCtrl.pageData.imageUrl, function(result) {
                    ui.button.check.main.enable();
                    tags.main = result;
                    displayInfo();
                });
            },
        },
        supporting: {
            all: function() {

            },
            location: function() {

            },
        },
        getTags: function(url, onReady) {
            let tempTmg = document.createElement('img');
            tempTmg.src = url.replace("http:", "https:");
            tempTmg.style.visibility = "hidden";
            tempTmg.onload = function() {
                EXIF.getData(tempTmg, function() { onReady(EXIF.getAllTags(this)); });
            };
        },
    },
    convert: {
        portal: function() {
            let convertedPortalLocation = geoKit.convertToWGS84(process.subCtrl.pageData.lat, process.subCtrl.pageData.lng);
            ui.button.disable(ui.button.convert.portal);
            ui.button.convert.portal.html("Converted");
            if ($.trim(ui.div.coordinateResult.html())) ui.div.coordinateResult.append("<br/>");
            if (tags.main) {
                let exifLocation = tags.parseLocation(tags.main);
                ui.div.coordinateResult.append("Converted Portal ↔︎ Original Exif: " + geoKit.getDistance(convertedPortalLocation.lat, convertedPortalLocation.lng, exifLocation.lat, exifLocation.lng).toFixed(2) + "m ");
            } else {
                ui.div.coordinateResult.append("Converted Portal: ");
            }
            let buttonShowMarker = $('<span class="clickable ingress-mid-blue">[Marker]</span>');
            buttonShowMarker.click(function() { ui.map.showMarker(convertedPortalLocation, "CP", "Converted Portal Location"); });
            ui.div.coordinateResult.append(buttonShowMarker);
        },
        main: function() {
            let exifLocation = tags.parseLocation(tags.main);
            let convertedExifLocation = geoKit.convertToWGS84(exifLocation.lat, exifLocation.lng);
            ui.button.disable(ui.button.convert.main);
            ui.button.convert.main.html("Converted");
            if ($.trim(ui.div.coordinateResult.html())) ui.div.coordinateResult.append("<br/>");
            ui.div.coordinateResult.append("Converted Exif ↔︎ Original Portal: " + geoKit.getDistance(subCtrl.pageData.lat, subCtrl.pageData.lng, convertedExifLocation.lat, convertedExifLocation.lng).toFixed(2) + "m ")
            let buttonShowMarker = $('<span class="clickable ingress-mid-blue">[Marker]</span>');
            buttonShowMarker.click(function() { ui.map.showMarker(convertedExifLocation, "CE", "Converted Exif Location"); });
            ui.div.coordinateResult.append(buttonShowMarker);
        },
        supporting: function() {

        },
    },
};

$("portalphoto:first").find("div").find(".center-cropped-img").one("load", process.onload);

window.onload = process.onload;