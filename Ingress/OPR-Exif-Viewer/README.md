# Exif Viewer for Ingress OPR
View the exif metadata and check where the photo was taken.

## Function
- Decode the exif metadata
- View the exif metadata in JSON
- Check the location if the data exists, calculate the distance from the portal's location and show a marker on the map below

## Usage
To use the script, click [here](https://lucka.moe/toolkit/ingress/OPR-Exif-Viewer.user.js) and install it with userscript manager like Tampermonkey, then there will be two new buttons on the OPR page, under the descriptions.

### Notice
- It may takes a while to fetch the full-size picture and decode the exif metadata, so be a little patient please.
- Maybe the location exif data is not common as you (or we) image, so don't be depressed, it's still helpful sometimes.

## Preview
| Full exif Metadata | Check Location
| :---: | :---:
| ![](Preview-All.png) | ![](Preview-Location.png)

## Dependencies & References
### Library
- [Exif.js](https://github.com/exif-js/exif-js)  
  A JavaScript library for reading EXIF meta data from image files.

### References
- [SmartIntel/opr_show_exif_info.user.js](https://github.com/DeepAQ/SmartIntel/blob/master/opr_show_exif_info.user.js)  
  Another exif viewer for OPR, learned how to use exif.js correctly.
- OPR_brainStroming  
  Useful plug-in for OPR, learned how to fetch the data of the portal.


## Changelog
```markdown
### [0.1.2] - 2018-12-01
#### Changed
- Optimized, prevent redundant decoding
```

```markdown
### [0.1.1] - 2018-12-01
#### Added
- Marker of the exif location on the map

#### Removed
- Azimuth
```

```markdown
### [0.1.0] - 2018-12-01
- Initial version
```

## Licence
This userscript is released under the [MIT License](../../LICENSE).
