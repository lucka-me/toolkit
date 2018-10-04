// Your package here

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.location.Criteria
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Bundle
import android.provider.Settings
import android.support.v4.app.ActivityCompat
import kotlin.math.*

/**
 * ```
 * MIT License
 *
 * Copyright (c) 2017-2018 Lucka
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 * ```
 *
 * This class provides a simple way to get location updates in Android, it encapsulates the [LocationManager] and [LocationListener], provides simplified interface and useful methods.
 *
 * ## Usage
 * - Create a new file and paste the code instead of adding the file to your project directly.
 * - Follow the code analysis of IDE to edit, fix or remove the code.
 * - The details of the methods are included in the code, documented in KDoc.
 *
 * ## Attributes
 * ### Public
 * - [lastLocation]
 * - [isLocationAvailable]
 * ### Private
 * - [_lastLocation]
 * - [locationManager]
 * - [currentProvider]
 * - [criteria]
 * - [locationListener]
 * - [assistLocationListener]
 * ### Static
 * - [ELLIPSOID_A]
 * - [ELLIPSOID_EE]
 * - [EARTH_R]
 * - [UPDATE_DISTANCE]
 * - [UPDATE_INTERVAL]
 * - [FIXED_PROVIDER]
 * - [DEFAULT_LONGITUDE]
 * - [DEFAULT_LATITUDE]
 *
 * ## Interface
 * - [locationKitListener]
 *
 * ## Methods
 * ### Public
 * - [startUpdate]
 * - [stopUpdate]
 * ### Private
 * - [startUpdateAssist]
 * ### Static
 * - [fixCoordinate]
 * - [requestPermission]
 *
 * ## Changelog
 * ### 0.1.0
 * - Initial version
 * ### 0.1.1
 * - Removed mock location detecting
 * - Make [lastLocation] a getter
 *
 * @param [context] The context
 * @param [locationKitListener] The interface, see [LocationKitListener]
 *
 * @author lucka-me
 * @since 0.1.0
 *
 * @property [_lastLocation] The last location with fixed (GCJ-02) coordinates
 * @property [lastLocation] The getter for last location with fixed (GCJ-02) coordinates ([_lastLocation])
 * @property [isLocationAvailable] If the location is available
 * @property [locationManager] The original [LocationManager]
 * @property [currentProvider] The location provider in use
 * @property [criteria] The requirement to get the best location provider
 * @property [locationListener] The original [LocationListener]
 * @property [assistLocationListener] Assistant [LocationListener], used to listen to the old provider when it's disabled and switched to another, and notify the [locationListener] when the old provider is enabled.
 * @property [ELLIPSOID_A] Semi-major of the earth ellipsoid in meter
 * @property [ELLIPSOID_EE] Flatness of the earth ellipsoid in meter
 * @property [EARTH_R] Average radius of the earth
 * @property [UPDATE_DISTANCE] Minimum distance between two location updates in meter
 * @property [UPDATE_INTERVAL] Minimum time interval between two location updates in millisecond
 * @property [FIXED_PROVIDER] The provider string to mark the fixed (GCJ-02) location
 * @property [DEFAULT_LONGITUDE] Alternative longitude when failed to get the very first location (Center of Xi'an City)
 * @property [DEFAULT_LATITUDE] Alternative latitude when failed to get the very first location (Center of Xi'an City)
 */
class LocationKit(
    private var context: Context,
    private val locationKitListener: LocationKitListener
) {

    private var _lastLocation: Location = Location(FIXED_PROVIDER)
    val lastLocation
        get() = Location(_lastLocation)
    var isLocationAvailable: Boolean = false
    private val locationManager =
        context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
    private var currentProvider = LocationManager.GPS_PROVIDER
    private val criteria = Criteria()
    private val locationListener = object : LocationListener {

        override fun onLocationChanged(location: Location?) {

            if (location == null) {
                isLocationAvailable = false
                return
            }
            _lastLocation = fixCoordinate(location)
            isLocationAvailable = true
            locationKitListener.onLocationUpdated(lastLocation)
        }

        override fun onProviderDisabled(provider: String?) {

            if (provider == currentProvider) {
                val newProvider = locationManager.getBestProvider(criteria ,true)
                if (newProvider != LocationManager.GPS_PROVIDER &&
                    newProvider != LocationManager.NETWORK_PROVIDER
                ) {
                    locationKitListener.onProviderDisabled()
                } else {
                    val oldProvider = currentProvider
                    currentProvider = newProvider
                    stopUpdate()
                    startUpdate(false)
                    startUpdateAssist(oldProvider)
                    locationKitListener.onProviderSwitchedTo(currentProvider)
                }
            }
        }

        override fun onProviderEnabled(provider: String?) {

            val newProvider = locationManager.getBestProvider(criteria ,true)
            if (newProvider != LocationManager.GPS_PROVIDER &&
                newProvider != LocationManager.NETWORK_PROVIDER
            ) {
                locationKitListener.onProviderDisabled()
                currentProvider = LocationManager.GPS_PROVIDER
            } else if (newProvider != currentProvider) {
                currentProvider = newProvider
                stopUpdate()
                startUpdate(false)
                locationKitListener.onProviderSwitchedTo(currentProvider)
            } else {
                locationKitListener.onProviderEnabled()
            }

        }

        override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {

        }
    }

    private val assistLocationListener = object : LocationListener {
        override fun onProviderEnabled(provider: String?) {
            locationListener.onProviderEnabled(provider)
            locationManager.removeUpdates(this)
        }
        override fun onLocationChanged(location: Location?) {}
        override fun onProviderDisabled(provider: String?) {}
        override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {}
    }

    /**
     * Interface used to receive notifications from [LocationKit]
     *
     * ## Public Methods
     * - [onLocationUpdated]
     * - [onProviderDisabled]
     * - [onProviderEnabled]
     * - [onProviderSwitchedTo]
     * - [onException]
     *
     * @author lucka-me
     * @since 0.1.0
     */
    interface LocationKitListener {
        /**
         * Called when the location has updated.
         *
         * The [lastLocation] and [isLocationAvailable] will be also updated when this method is called
         *
         * @author lucka-me
         * @since 0.1.0
         */
        fun onLocationUpdated(location: Location)
        /**
         * Called when both GPS Provider and Network Provider are disabled.
         *
         * Usually fired when user turn off the location from System Settings.
         *
         * @author lucka-me
         * @since 0.1.0
         */
        fun onProviderDisabled()
        /**
         * Called when either GPS Provider or Network Provider is enabled.
         *
         * Usually fired when user turn on the location from System Settings.
         *
         * @author lucka-me
         * @since 0.1.0
         */
        fun onProviderEnabled()
        /**
         * Called when location provider is switched automatically.
         *
         * @param [newProvider] The new provider in use
         *
         * @author lucka-me
         * @since 0.1.0
         */
        fun onProviderSwitchedTo(newProvider: String)
        /**
         * Called when, and the resource id of error message:
         * - A mock location is detected -> [R.string.err_location_mock]
         * - Location permission is denied -> [R.string.err_location_permission_denied]
         *
         * @author lucka-me
         * @since 0.1.0
         */
        fun onException(error: Exception)
    }

    init {
        criteria.accuracy = Criteria.ACCURACY_FINE
        if (ActivityCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) ==
            PackageManager.PERMISSION_GRANTED
        ) {
            // Must get one whatever the provider is
            val location = locationManager
                .getLastKnownLocation(locationManager.getBestProvider(criteria, true))
            if (location == null) {
                _lastLocation.longitude = DEFAULT_LONGITUDE
                _lastLocation.latitude = DEFAULT_LATITUDE
                isLocationAvailable = false
            } else {
                _lastLocation = fixCoordinate(location)
                isLocationAvailable = true
            }
        } else {
            _lastLocation.longitude = DEFAULT_LONGITUDE
            _lastLocation.latitude = DEFAULT_LATITUDE
            isLocationAvailable = false
        }
    }

    /**
     * Start location updates, using [UPDATE_DISTANCE] and [UPDATE_INTERVAL].
     *
     * @param [resetProvider] If should get the best enabled provider first
     *
     * @return If the update is started successfully
     *
     * @author lucka-me
     * @since 0.1.0
     */
    fun startUpdate(resetProvider: Boolean = true): Boolean {
        if (resetProvider) {
            val newProvider = locationManager.getBestProvider(criteria ,true)
            if (newProvider == LocationManager.GPS_PROVIDER ||
                newProvider == LocationManager.NETWORK_PROVIDER
            ) {
                currentProvider = newProvider
            }
        }
        return if (ActivityCompat
                .checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) ==
            PackageManager.PERMISSION_GRANTED
        ) {
            locationManager.requestLocationUpdates(
                currentProvider,
                UPDATE_INTERVAL,
                UPDATE_DISTANCE,
                locationListener
            )
            true
        } else {
            val error = Exception(context.getString(R.string.err_location_permission_denied))
            locationKitListener.onException(error)
            false
        }
    }

    /**
     * Stop location updates.
     *
     * @author lucka-me
     * @since 0.1.4
     */
    fun stopUpdate() {
        locationManager.removeUpdates(locationListener)
    }

    /**
     * Start to listen to the appointed provider with [assistLocationListener], which will notify the [locationListener] only when the provider is enabled.
     *
     * @param [provider] The provider needs to be listened
     *
     * @author lucka-me
     * @since 0.1.0
     */
    private fun startUpdateAssist(provider: String) {
        if (ActivityCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) ==
            PackageManager.PERMISSION_GRANTED
        ) {
            locationManager.requestLocationUpdates(
                provider,
                UPDATE_INTERVAL,
                UPDATE_DISTANCE,
                assistLocationListener
            )
        } else {
            val error = Exception(context.getString(R.string.err_location_permission_denied))
            locationKitListener.onException(error)
        }
    }

    companion object {
        const val ELLIPSOID_A = 6378137.0
        const val ELLIPSOID_EE = 0.00669342162296594323
        const val EARTH_R = 6372796.924
        const val UPDATE_INTERVAL: Long = 1000
        const val UPDATE_DISTANCE: Float = 2.0f
        const val FIXED_PROVIDER = "fixed"
        const val DEFAULT_LONGITUDE = 108.947031
        const val DEFAULT_LATITUDE = 34.259441

        /**
         * Convert (Fix) location from WGS-84 to GCJ-02.
         *
         * Note: The original method of the original method is licensed under MIT License, I have no idea what should I do here (put the license here or not) yet.
         *
         * @param [location] Location to be fixed
         *
         * @return Fixed location
         *
         * @see <a href="https://github.com/geosmart/coordtransform/blob/master/src/main/java/me/demo/util/geo/CoordinateTransformUtil.java">Original method | Github</a>
         *
         * @author lucka-me
         * @since 0.1.0
         */
        fun fixCoordinate(location: Location): Location {
            // Avoid fixing redundantly
            if (location.provider == FIXED_PROVIDER) return Location(location)
            val origLat = location.latitude
            val origLng = location.longitude
            // Avoid fix when the location is oversea
            if ((origLng < 72.004 || origLng > 137.8347) ||
                (origLat < 0.8293 || origLat > 55.8271)
            ) {
                val newLocation = Location(location)
                newLocation.provider = FIXED_PROVIDER
                return newLocation
            }
            val lat = origLat - 35.0
            val lng = origLng - 105.0
            var dLat = (-100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat
                + 0.2 * sqrt(abs(lng))
                + (20.0 * sin(6.0 * lng * PI) + 20.0 * sin(2.0 * lng * PI))
                * 2.0 / 3.0 + (20.0 * sin(lat * PI) + 40.0 * sin(lat / 3.0 * PI))
                * 2.0 / 3.0 + (160.0 * sin(lat / 12.0 * PI)
                + 320 * sin(lat * PI / 30.0)) * 2.0 / 3.0)
            var dLng = (300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1
                * sqrt(abs(lng)) + (20.0 * sin(6.0 * lng * PI) + 20.0
                * sin(2.0 * lng * PI)) * 2.0 / 3.0 + (20.0 * sin(lng * PI) + 40.0
                * sin(lng / 3.0 * PI)) * 2.0 / 3.0 + (150.0 * sin(lng / 12.0 * PI)
                + 300.0 * sin(lng / 30.0 * PI)) * 2.0 / 3.0)
            val radLat = origLat / 180.0 * PI
            var magic = sin(radLat)
            magic = 1 - ELLIPSOID_EE * magic * magic
            val sqrtMagic = sqrt(magic)
            dLat = (dLat * 180.0) / ((ELLIPSOID_A * (1 - ELLIPSOID_EE)) / (magic * sqrtMagic) * PI)
            dLng = (dLng * 180.0) / (ELLIPSOID_A / sqrtMagic * cos(radLat) * PI)
            val fixedLat = origLat + dLat
            val fixedLng = origLng + dLng
            val newLocation = Location(location)
            newLocation.provider = FIXED_PROVIDER
            newLocation.latitude = fixedLat
            newLocation.longitude = fixedLng
            return newLocation
        }

        /**
         * Request location permission.
         *
         * @param [activity] Activity of the application
         * @param [requestCode] Request code for Request Permissions Result Callback
         *
         * @return If the permission is denied before and needs a explanation
         *
         * @author lucka-me
         * @since 0.1.5
         */
        fun requestPermission(activity: MainActivity, requestCode: Int): Boolean {
            if (ActivityCompat
                    .checkSelfPermission(activity, Manifest.permission.ACCESS_FINE_LOCATION) !=
                PackageManager.PERMISSION_GRANTED
            ) {
                // Explain if permission denied before
                if (ActivityCompat.shouldShowRequestPermissionRationale(
                        activity,
                        Manifest.permission.ACCESS_FINE_LOCATION
                    )
                ) {
                    return true
                } else {
                    ActivityCompat.requestPermissions(
                        activity,
                        arrayOf(Manifest.permission.ACCESS_FINE_LOCATION),
                        requestCode
                    )
                }
            }
            return false
        }
    }
}
