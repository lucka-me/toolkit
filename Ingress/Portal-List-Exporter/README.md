# IITC Plugin: Portal List Exporter

A simple IITC plugin to:

1. Export portals as:
    ```jsonc
    [
        {
            "guid": "GUID of Portal",
            "title": "Title of Portal",
            "lngLat": {
                "lng": 90.0,    // Longitude
                "lat": 45.0     // Latitude
            }
        },
        // ...
    ]
    ```
2. Export keys in inventory (requires [Live Inventory Plugin](https://github.com/EisFrei/IngressLiveInventory)) as:
    ```jsonc
    [
        "GUID of Portal",
        // ...
    ]
    ```

## Changelog

### [0.1.0] - 2022-04-30
- Initial version

</p>
</details>

## Licence
This userscript is released under the [MIT License](../../LICENSE).
