// ==UserScript==
// @id portal-list-exporter.user
// @name IITC Plugin: Portal List Exporter
// @category Misc
// @version 1.0.0
// @namespace https://lucka.moe/iitc/portal-list-exporter
// @description Utility for Ingress Drone Explorer
// @include https://intel.ingress.com/intel*
// @match https://intel.ingress.com/intel*
// @grant none
// ==/UserScript==

function wrapper(plugin_info) {
    if (typeof window.plugin !== 'function') window.plugin = function () { };

    const plugin = window.plugin.portalListExporter = function() { };
    
    plugin.exportPortalList = function() {
        const list = [];
        for (key in window.portals) {
            const value = window.portals[key];
            list.push({
                guid: key,
                title: value.options.data.title,
                lngLat: {
                    lng: value._latlng.lng,
                    lat: value._latlng.lat,
                }
            });
        }
        const center = window.map.getCenter();
        window.saveFile(
            JSON.stringify(list),
            `portal-list-${Date.now()}-${center.lng},${center.lat}z${window.map.getZoom()}.json`,
            'application/json'
        );
        window.alert(`Exported ${list.length} portal(s)`);
    };

    plugin.exportKeyList = function() {
        const keys = window.plugin.LiveInventory.keyCount;
        const list = [];
        for (index in keys) {
            list.push(keys[index].portalCoupler.portalGuid);
        }
        window.saveFile(
            JSON.stringify(list),
            `key-list-${Date.now()}.json`,
            'application/json'
        );
        window.alert(`Exported ${list.length} key(s)`);
    };

    plugin.openPanel = function() {
        let html = '<div>';
        html += '<button type="button" onclick="window.plugin.portalListExporter.exportPortalList()">Export Portal List</button>';
        if (window.plugin.LiveInventory) {
            html += '<button type="button" onclick="window.plugin.portalListExporter.exportKeyList()">Export Key List</button>';
        }
        html += '</div>';
        window.dialog({
            id: 'portal-list-exporter-panel',
            title: 'Portal List Exporter',
            html: html
        });
    };

    function setup() {
        $('#toolbox').append('<a onclick="window.plugin.portalListExporter.openPanel()">Portal List Exporter</a>');
    }

    setup.info = plugin_info;

    if (!window.bootPlugins) window.bootPlugins = [];
    window.bootPlugins.push(setup);
    if (window.iitcLoaded && typeof setup === 'function') setup();
}

var script = document.createElement('script');
var info = {};

if (typeof GM_info !== 'undefined' && GM_info && GM_info.script) {
    info.script = {
        version: GM_info.script.version,
        name: GM_info.script.name,
        description: GM_info.script.description
    };
}

var textContent = document.createTextNode('(' + wrapper + ')(' + JSON.stringify(info) + ')');
script.appendChild(textContent);
(document.body || document.head || document.documentElement).appendChild(script);