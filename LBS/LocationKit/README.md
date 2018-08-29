# LocationKit
A simple way to get location updates in Android.

This class encapsulates the [`LocationManager`](https://developer.android.com/reference/android/location/LocationManager "Android Developers") and [`LocationListener`](https://developer.android.com/reference/android/location/LocationListener "LocationListener | Android Developers"), provides simplified interface and useful methods.

The code is written in Kotlin because I dont' know anything about Java... Maybe I'll write a Java version or even other languages in the future, mainly depends on my need.

The code was born in my recent project [RoundO-android](https://github.com/lucka-me/RoundO-android "GitHub"), and has been applied into another project of mine called [Patroute-android](https://github.com/lucka-me/Patroute-android "GitHub"), works fine, yet.

## Functions
- A **non-nullable** `lastLocation` with boolean `isLocationAvailable`
- Switch between `GPS_PROVIDER` and `NETWORK_PROVIDER` **automatically**
- Convert location from WGS-84 to GCJ-02 when location updated (Original method [here](https://github.com/geosmart/coordtransform/blob/master/src/main/java/me/demo/util/geo/CoordinateTransformUtil.java "GitHub"))
- A static method to request location permission

## Requirements
* Kotlin support

## Usage
* Create a new file and paste the code instead of adding the file to your project directly.
* Follow the code analysis of IDE to edit, fix or remove the code.
* The details of the methods are included in the code, documented in KDoc.

### Notice
* It's highly possible that you have to edit or remove the `fixLocation()` and related code
  * If you're using a non-Mainland map using WGS-84 like Google Maps, you **must** remove the function and related code
  * If you're using a map using encryption method based on GCJ-02 like Baidu Map, you **must** replace the convert method with the method provided with the map API
  * If you're using a map using GCJ-02 like AMap, you're still **highly recommended** to replace the convert method with the method provided with the map API if there is one

## Changelog
```markdown
### [0.1.0] - 2018-08-29
- Initial version
```

## Licence
The code is released under [MIT License](../../LICENSE)。
