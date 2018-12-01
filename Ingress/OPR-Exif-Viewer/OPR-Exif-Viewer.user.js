// ==UserScript==
// @name         OPR Exif Viewer
// @namespace    http://lucka.moe/
// @version      0.1
// @author       lucka-me
// @homepageURL  https://github.com/lucka-me/toolkit/tree/master/Ingress/OPR-Exif-Viewer
// @match        https://opr.ingress.com/recon
// @grant        none
// @require      https://cdn.jsdelivr.net/npm/exif-js
// ==/UserScript==

var detectImgLoaded = false;
var distanceShown = false;
var detectImg = null;

var dmsToDeg = function(dms) {
    var d = dms[0];
    var m = dms[1];
    var s = dms[2];
    return Math.round((d / 1 + m / 60 + s / 3600) * 1E6) / 1E6;
}

// Ref: https://stackoverflow.com/a/1502821/10276204
var getDistance = function(p1Lat, p1Lng, p2Lat, p2Lng) {
  var R = 6378137; // Earth’s mean radius in meter
  var dLat = (p2Lat - p1Lat) * Math.PI / 180;
  var dLng = (p2Lng - p1Lng) * Math.PI / 180;
  var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(p1Lat * Math.PI / 180) * Math.cos(p2Lat * Math.PI / 180) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  var d = R * c;
  return d;
};

var getAzimuth = function(p1Lat, p1Lng, p2Lat, p2Lng) {
    var radLat1 = p1Lat * Math.PI / 180;
    var radLng1 = p1Lng * Math.PI / 180;
    var radLat2 = p2Lat * Math.PI / 180;
    var radLng2 = p2Lng * Math.PI / 180;
    var dLng = radLng2 - radLng1;
    var azimuth = Math.atan2(Math.sin(dLng) * Math.cos(radLat2), Math.cos(radLat1) * Math.sin(radLat2) - Math.sin(radLat1) * Math.cos(radLat2) * Math.cos(dLng)) * 180 / Math.PI;
    if (azimuth < 0) azimuth += 360;
    return azimuth;
}

var loadDetectImg = function(onload) {
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
        detectImgLoaded = true;
        detectImg = newImg;
        buttonCheckExifAll.disabled = false;
        buttonCheckExifAll.innerHTML = "Check All";
        buttonCheckExifLocation.disabled = false;
        buttonCheckExifLocation.innerHTML = "Check Location";
        onload(detectImg);
    };
}

var checkExifAll = function(targetImage) {
    EXIF.getData(targetImage, function() {
        var buttonCheckExifAll = document.getElementById("buttonCheckExifAll");
        buttonCheckExifAll.disabled = false;
        buttonCheckExifAll.innerHTML = "Check All";
        var allTags = EXIF.getAllTags(this);
        alert(JSON.stringify(allTags, null, "\t"));
    });
}

window.onCheckExifAll = function() {
    if (detectImgLoaded) {
        checkExifAll(detectImg);
        return;
    }
    loadDetectImg(checkExifAll);
}

var checkExifLocation = function(targetImage) {
    EXIF.getData(targetImage, function() {
        var buttonCheckExifLocation = document.getElementById("buttonCheckExifLocation");
        var allTags = EXIF.getAllTags(this);
        if (allTags.GPSLatitude && allTags.GPSLongitude) {
            var latitude = (allTags.GPSLatitudeRef == "N" ? 1 : -1) * dmsToDeg(allTags.GPSLatitude);
            var longitude = (allTags.GPSLongitudeRef == "E" ? 1 : -1) * dmsToDeg(allTags.GPSLongitude);
            if (!distanceShown) {
                var subCtrl = angular.element(document.getElementById('NewSubmissionController')).scope().subCtrl;
                $("#descriptionDiv").append("<br/>Distance: " + getDistance(subCtrl.pageData.lat, subCtrl.pageData.lng, latitude, longitude).toFixed(2) + "m");
                $("#descriptionDiv").append("<br/>Azimuth: " + getAzimuth(subCtrl.pageData.lat, subCtrl.pageData.lng, latitude, longitude).toFixed(2));
                distanceShown = true;
            }
            buttonCheckExifLocation.disabled = true;
            buttonCheckExifLocation.innerHTML = "Location Checked";
        } else {
            buttonCheckExifLocation.disabled = true;
            buttonCheckExifLocation.innerHTML = "No Location Data";
        }
    });
}

window.onCheckExifLocation = function() {
    if (detectImgLoaded) {
        checkExifLocation(detectImg);
        return;
    }
    loadDetectImg(checkExifLocation);
};

window.onload = function() {
    var descDiv = $("#descriptionDiv");
    descDiv.append("<br/><small class=\"gold\">EXIF</small><br/>");
    descDiv.append("<button type=\"button\" class=\"button\" id=\"buttonCheckExifAll\" onclick=\"onCheckExifAll()\">Check All</button>")
    descDiv.append("<button type=\"button\" class=\"button\" id=\"buttonCheckExifLocation\" onclick=\"onCheckExifLocation()\">Check Location</button>");
};
