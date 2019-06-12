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
                disable: function() {
                    ui.button.disable(ui.button.check.supporting.all);
                    ui.button.check.supporting.all.html("Loading Image");
                    ui.button.disable(ui.button.check.supporting.location);
                    ui.button.check.supporting.location.html("Loading Image");
                },
                enable: function() {
                    ui.button.enable(ui.button.check.supporting.all);
                    ui.button.check.supporting.all.html("All (Supporting)");
                    ui.button.enable(ui.button.check.supporting.location);
                    ui.button.check.supporting.location.html("Location (Supporting)");
                },
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
        if (!detect.pageData) return;
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

        if (preferences.autoRun) process.check.main;
    },
    check: {
        main: {
            all: function() { process.check.all("main", process.subCtrl.pageData.imageUrl); },
            location: function() { process.check.location("main", process.subCtrl.pageData.imageUrl, { label: "E", title: "Exif Location"}); },
        },
        supporting: {
            all: function() { process.check.all("supporting", process.subCtrl.pageData.supportingImageUrl); },
            location: function() { process.check.location("supporting", process.subCtrl.pageData.supportingImageUrl, { label: "SE", title: "Supporting Exif Location"}); },
        },
        getTags: function(type, url, onReady) {
            let tempTmg = document.createElement('img');
            tempTmg.style.visibility = "hidden";
            tempTmg.onload = function() {
                EXIF.getData(tempTmg, function() {
                    ui.button.check[type].enable();
                    tags[type] = EXIF.getAllTags(this);
                    onReady();
                });
            };
            tempTmg.src = url.replace("http:", "https:") + "=s0";
        },
        all: function(type, imageUrl) {
            let displayAll = function() { alert(JSON.stringify(tags[type], null, "\t")); };
            if (tags[type]) {
                displayAll();
                return;
            }
            ui.button.check[type].disable();
            process.check.getTags(type, imageUrl, displayAll);
        },
        location: function(type, imageUrl, markerString) {
            let displayInfo = function() {
                ui.button.disable(ui.button.check[type].location);
                if (tags[type].GPSLatitude && tags[type].GPSLongitude) {
                    let location = tags.parseLocation(tags[type]);
                    ui.div.exifResult.append(
                        "Distance: " + geoKit.getDistance(subCtrl.pageData.lat, subCtrl.pageData.lng, location.lat, location.lng).toFixed(2) + "m "
                    );
                    let buttonShowMarker = $('<span class="clickable ingress-mid-blue">[Marker]</span>');
                    buttonShowMarker.click(function() { ui.map.showMarker(location, markerString.label, markerString.title); });
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
            if (tags[type]) {
                displayInfo();
                return;
            }
            ui.button.check[type].disable();
            process.check.getTags(type, imageUrl, displayInfo);
        }
    },
    convert: {
        portal: function() {
            let convertedPortalLocation = geoKit.convertToWGS84(process.subCtrl.pageData.lat, process.subCtrl.pageData.lng);
            ui.button.disable(ui.button.convert.portal);
            ui.button.convert.portal.html("Converted");
            if ($.trim(ui.div.coordinateResult.html())) ui.div.coordinateResult.append("<br/>");
            if (tags.main) {
                let exifLocation = tags.parseLocation(tags.main);
                ui.div.coordinateResult.append("Converted Portal ?? Original Exif: " + geoKit.getDistance(convertedPortalLocation.lat, convertedPortalLocation.lng, exifLocation.lat, exifLocation.lng).toFixed(2) + "m ");
            } else {
                ui.div.coordinateResult.append("Converted Portal: ");
            }
            let buttonShowMarker = $('<span class="clickable ingress-mid-blue">[Marker]</span>');
            buttonShowMarker.click(function() { ui.map.showMarker(convertedPortalLocation, "CP", "Converted Portal Location"); });
            ui.div.coordinateResult.append(buttonShowMarker);
        },
        main: function() { process.convert.exif("main", { prefix: "Converted", markerLabel: "CE" }); },
        supporting: function() { process.convert.exif("supporting", { prefix: "Converted Supporting", markerLabel: "CSE" }); },
        exif: function(type, strings) {
            let exifLocation = tags.parseLocation(tags[type]);
            let convertedExifLocation = geoKit.convertToWGS84(exifLocation.lat, exifLocation.lng);
            ui.button.disable(ui.button.convert[type]);
            ui.button.convert[type].html("Converted");
            if ($.trim(ui.div.coordinateResult.html())) ui.div.coordinateResult.append("<br/>");
            ui.div.coordinateResult.append(strings.prefix + " Exif ?? Original Portal: " + geoKit.getDistance(subCtrl.pageData.lat, subCtrl.pageData.lng, convertedExifLocation.lat, convertedExifLocation.lng).toFixed(2) + "m ")
            let buttonShowMarker = $('<span class="clickable ingress-mid-blue">[Marker]</span>');
            buttonShowMarker.click(function() { ui.map.showMarker(convertedExifLocation, strings.markerLabel, strings.prefix + " Exif Location"); });
            ui.div.coordinateResult.append(buttonShowMarker);
        }
    },
};

$("portalphoto:first").find("div").find(".center-cropped-img").one("load", process.onload);

window.onload = process.onload;