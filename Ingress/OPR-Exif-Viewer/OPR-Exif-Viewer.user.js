// ==UserScript==
// @name         OPR Exif Viewer
// @namespace    http://lucka.moe/
// @version      0.1.6
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
var preferences = {
    autoRun: false // Set to true if you want to get exif automatically when the page is loaded
};
// Preferences ABOVE

var isScriptLoaded = false;
var distanceShown = false;
var exifTags = null;
var detectLocation = null;
var wgs84ExifLocation = null;
var wgs84PortalLocation = null;

var dmsToDeg = function(dms) {
    var d = dms[0];
    var m = dms[1];
    var s = dms[2];
    return Math.round((d / 1 + m / 60 + s / 3600) * 1E6) / 1E6;
}

// Ref: https://stackoverflow.com/a/1502821/10276204
var getDistance = function(p1Lat, p1Lng, p2Lat, p2Lng) {
  var dLat = (p2Lat - p1Lat) * Math.PI / 180;
  var dLng = (p2Lng - p1Lng) * Math.PI / 180;
  var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(p1Lat * Math.PI / 180) * Math.cos(p2Lat * Math.PI / 180) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return 6378137 * c;
};

// Ref: https://github.com/googollee/eviltransform/blob/master/javascript/transform.js
var convertToWGS84 = function(fromLat, fromLng) {
    var transform = function(x, y) {
        var xy = x * y;
        var absX = Math.sqrt(Math.abs(x));
        var xPi = x * Math.PI;
        var yPi = y * Math.PI;
        var d = 20.0*Math.sin(6.0*xPi) + 20.0*Math.sin(2.0*xPi);
        var lat = d;
        var lng = d;
        lat += 20.0*Math.sin(yPi) + 40.0*Math.sin(yPi/3.0);
        lng += 20.0*Math.sin(xPi) + 40.0*Math.sin(xPi/3.0);
        lat += 160.0*Math.sin(yPi/12.0) + 320*Math.sin(yPi/30.0);
        lng += 150.0*Math.sin(xPi/12.0) + 300.0*Math.sin(xPi/30.0);
        lat *= 2.0 / 3.0;
        lng *= 2.0 / 3.0;
        lat += -100.0 + 2.0*x + 3.0*y + 0.2*y*y + 0.1*xy + 0.2*absX;
        lng += 300.0 + x + 2.0*y + 0.1*x*x + 0.1*xy + 0.1*absX;
        return {lat: lat, lng: lng}
    }
    var delta = function(lat, lng) {
        var ee = 0.00669342162296594323;
        var d = transform(lng-105.0, lat-35.0);
        var radLat = lat / 180.0 * Math.PI;
        var magic = Math.sin(radLat);
        magic = 1 - ee*magic*magic;
        var sqrtMagic = Math.sqrt(magic);
        d.lat = (d.lat * 180.0) / ((6378137 * (1 - ee)) / (magic * sqrtMagic) * Math.PI);
        d.lng = (d.lng * 180.0) / (6378137 / sqrtMagic * Math.cos(radLat) * Math.PI);
        return d;
    }
    var d = delta(fromLat, fromLng);
    return new google.maps.LatLng(fromLat - d.lat, fromLng - d.lng);
}

var getExifTags = function(onGet) {
    var buttonCheckExifAll = document.getElementById("buttonCheckExifAll");
    var buttonCheckExifLocation = document.getElementById("buttonCheckExifLocation");
    buttonCheckExifAll.disabled = true;
    buttonCheckExifAll.innerHTML = "Loading Image";
    buttonCheckExifLocation.disabled = true;
    buttonCheckExifLocation.innerHTML = "Loading Image";
    var imgUrl = $('.center-cropped-img').attr('src');
    if (!imgUrl) {
        buttonCheckExifAll.disabled = false;
        buttonCheckExifAll.innerHTML = "Check All";
        buttonCheckExifLocation.disabled = false;
        buttonCheckExifLocation.innerHTML = "Check Location";
        return;
    }
    var newImg = document.createElement('img');
    newImg.src = (imgUrl + "=s0").replace("http:", "https:");
    newImg.style.visibility = "hidden";
    newImg.onload = function() {
        EXIF.getData(newImg, function() {
            exifTags = EXIF.getAllTags(this);
            buttonCheckExifAll.disabled = false;
            buttonCheckExifAll.innerHTML = "Check All";
            buttonCheckExifLocation.disabled = false;
            buttonCheckExifLocation.innerHTML = "Check Location";
            onGet(exifTags);
        });
    };
}

var checkExifAll = function(tags) {
    alert(JSON.stringify(tags, null, "\t"));
}

window.onCheckExifAll = function() {
    if (exifTags != null) {
        checkExifAll(exifTags);
        return;
    }
    getExifTags(checkExifAll);
}

window.showMarker = function() {
    var marker = new google.maps.Marker({
        position: detectLocation,
        map: subCtrl.map2,
        label: "E",
        title: "Exif Location"
    });
    subCtrl.map2.panTo(detectLocation);
}

window.showConvertedExifMarker = function() {
    var marker = new google.maps.Marker({
        position: wgs84ExifLocation,
        map: subCtrl.map2,
        label: "CE",
        title: "Converted Exif Location"
    });
    subCtrl.map2.panTo(wgs84ExifLocation);
}

window.convertExifCoordinate = function() {
    wgs84ExifLocation = convertToWGS84(detectLocation.lat(), detectLocation.lng());
    var buttonConvertExif = document.getElementById("buttonConvertExif");
    buttonConvertExif.disabled = true;
    buttonConvertExif.innerHTML = "Converted";
    var descDiv = $("#descriptionDiv");
    descDiv.append("<br/>Converted Exif ↔︎ Original Portal: " + getDistance(subCtrl.pageData.lat, subCtrl.pageData.lng, wgs84ExifLocation.lat(), wgs84ExifLocation.lng()).toFixed(2) + "m ")
    descDiv.append("<span class=\"clickable ingress-mid-blue\" onclick=\"showConvertedExifMarker()\">[Marker]</span>");
}

window.showConvertedPortalMarker = function() {
    var marker = new google.maps.Marker({
        position: wgs84PortalLocation,
        map: subCtrl.map2,
        label: "CP",
        title: "Converted Portal Location"
    });
    subCtrl.map2.panTo(wgs84PortalLocation);
}

window.convertPortalCoordinate = function() {
    wgs84PortalLocation = convertToWGS84(subCtrl.pageData.lat, subCtrl.pageData.lng);
    var buttonConvertPortal = document.getElementById("buttonConvertPortal");
    buttonConvertPortal.disabled = true;
    buttonConvertPortal.innerHTML = "Converted";
    var descDiv = $("#descriptionDiv");
    descDiv.append("<br/>Converted Portal ↔︎ Original Exif: " + getDistance(wgs84PortalLocation.lat(), wgs84PortalLocation.lng(), detectLocation.lat(), detectLocation.lng()).toFixed(2) + "m ")
    descDiv.append("<span class=\"clickable ingress-mid-blue\" onclick=\"showConvertedPortalMarker()\">[Marker]</span>");
}

var checkExifLocation = function(tags) {
    var buttonCheckExifLocation = document.getElementById("buttonCheckExifLocation");
    if (tags.GPSLatitude && tags.GPSLongitude) {
        detectLocation = new google.maps.LatLng(
            (tags.GPSLatitudeRef == "N" ? 1 : -1) * dmsToDeg(tags.GPSLatitude),
            (tags.GPSLongitudeRef == "E" ? 1 : -1) * dmsToDeg(tags.GPSLongitude)
        );
        if (!distanceShown) {
            var descDiv = $("#descriptionDiv");
            descDiv.append(
                "<br/>Distance: " + getDistance(subCtrl.pageData.lat, subCtrl.pageData.lng, detectLocation.lat(), detectLocation.lng()).toFixed(2) + "m "
            );
            descDiv.append("<span class=\"clickable ingress-mid-blue\" onclick=\"showMarker()\">[Marker]</span>");
            distanceShown = true;
            descDiv.append("<br/><small class=\"gold\">Coordinate Conversion</small><br/>");
            descDiv.append("<button type=\"button\" class=\"button\" id=\"buttonConvertExif\" onclick=\"convertExifCoordinate()\">Exif</button>");
            descDiv.append("<button type=\"button\" class=\"button\" id=\"buttonConvertPortal\" onclick=\"convertPortalCoordinate()\">Portal</button>");
        }
        buttonCheckExifLocation.disabled = true;
        buttonCheckExifLocation.innerHTML = "Location Checked";
    } else {
        buttonCheckExifLocation.disabled = true;
        buttonCheckExifLocation.innerHTML = "No Location Data";
    }
}

window.onCheckExifLocation = function() {
    if (exifTags != null) {
        checkExifLocation(exifTags);
        return;
    }
    getExifTags(checkExifLocation);
};

function loadOPREV() {
    if (isScriptLoaded) return;
    var descDiv = $("#descriptionDiv");
    descDiv.append("<br/><small class=\"gold\">EXIF</small><br/>");
    descDiv.append("<button type=\"button\" class=\"button\" id=\"buttonCheckExifAll\" onclick=\"onCheckExifAll()\">Check All</button>")
    descDiv.append("<button type=\"button\" class=\"button\" id=\"buttonCheckExifLocation\" onclick=\"onCheckExifLocation()\">Check Location</button>");
    isScriptLoaded = true;
    if (preferences.autoRun) {
        window.onCheckExifLocation();
    }
};

$("portalphoto:first").find("div").find(".center-cropped-img").one("load", loadOPREV);

window.onload = loadOPREV;
