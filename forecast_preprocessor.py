import pandas as pd
import math
import psychrolib # Psychrometric conversion library https://github.com/psychrometrics/psychrolib (Installation: https://pypi.org/project/PsychroLib/, Documentation: https://psychrometrics.github.io/psychrolib/api_docs.html)

class ForecastPreprocessor():

    def __init__(self) -> None:
        self.ROUGHNESS_LENGTH_Z0 = 0.03 # in meters from roughness class 1 (https://wind-data.ch/tools/profile.php?h=10&v=5&z0=0.03&abfrage=Refresh)
        self.REFERENCE_HEIGHT_H1 = 10.0 # in meters
        self.WIND_HEIGHT_H2 = 0.5 # in meters
        self.CORRECTING_FACTOR = math.log(self.WIND_HEIGHT_H2 / self.ROUGHNESS_LENGTH_Z0) / math.log(self.REFERENCE_HEIGHT_H1 / self.ROUGHNESS_LENGTH_Z0)

        self.route_df : pd.DataFrame = pd.DataFrame()
        self.forecast_df : pd.DataFrame = pd.DataFrame()
        self.forecast_preprocessed_df : pd.DataFrame = pd.DataFrame()

    def _cut_data(self):
        # cut data based on final time
        # create linear time column for algorithms
        # assign useful colum to self.forecast_preprocessed_df to be used in the next steps
        pass

    def _wind_log_correction(self) -> None:
        """
        Correct the wind speed forecast at 10 meters to the wind speed at 0.5 meters.
        Equation taken from: https://wind-data.ch/tools/profile.php?h=10&v=5&z0=0.03&abfrage=Refresh
        """
        wind_speed_corrected = pd.DataFrame(self.forecast_df['ff'] * self.CORRECTING_FACTOR, columns=['windSpeedCorrected']) # in km/h
        self.forecast_preprocessed_df = pd.concat([self.forecast_preprocessed_df, wind_speed_corrected], axis=1)

    def _wind_decomposition(self) -> None:
        theta = self.route_df['theta'] # in degrees
        wind_direction = self.forecast_df['dd'] # in degrees
        attack_angle = wind_direction - theta # in degrees

        wind_speed_side = pd.DataFrame(self.forecast_preprocessed_df['windSpeedCorrected'] * math.sin(math.radians(attack_angle)), columns=['sideWind']) # in km/h
        wind_speed_front = pd.DataFrame(self.forecast_preprocessed_df['windSpeedCorrected'] * math.cos(math.radians(attack_angle)), columns=['frontWind']) # in km/h

        self.forecast_preprocessed_df = pd.concat([self.forecast_preprocessed_df, wind_speed_side, wind_speed_front], axis=1)

    def _temperature_correction(self) -> None:
        """
        Correction suggest by Pascal Graf from Meteotest.
        """
        # Extract the time values from the multi-index
        times = self.forecast_df.index.get_level_values('time').hour

        # Apply corrections based on the time
        mask_night = (times >= 20) | (times <= 8)
        mask_day = (times >= 10) & (times <= 16)

        # Preallocate the temperature column
        temperature_corrected = pd.DataFrame(self.forecast_df['tt'], columns=['temperatureCorrected']) # in °C
        self.forecast_preprocessed_df = pd.concat([self.forecast_preprocessed_df, temperature_corrected], axis=1)

        # Apply the corrections
        self.forecast_preprocessed_df.loc[mask_night, 'temperatureCorrected'] += 3  # Add 3°C during the night
        self.forecast_preprocessed_df.loc[mask_day, 'temperatureCorrected'] -= 2    # Subtract 2°C during the day
        # No correction is applied for the in-between times as they remain unchanged

    def _air_density_estimation(self) -> None:
        """
        TODO https://wind-data.ch/tools/luftdichte.php?method=2&pr=990&t=25&rh=99&abfrage2=Aktualisieren
        """
        psychrolib.SetUnitSystem(psychrolib.SI)

        # Extract altitude data and calculate atmospheric pressure
        altitude = self.route_df['altitudeSmoothed'] # in meters
        atmospheric_pressure = psychrolib.GetStandardAtmPressure(Altitude=altitude) # in Pa

        # Extract temperature and relative humidity data and calculate humidity ratio
        air_temperature = self.forecast_df['tt'] # in °C
        relative_humidity = self.forecast_df['rh'] # in %
        humidity_ratio = psychrolib.GetHumRatioFromRelHum(TDryBulb=air_temperature, RelHum=relative_humidity/100, Pressure=atmospheric_pressure) # in kg_H₂O kg_Air⁻¹ [SI]

        # Calculate air density
        density = psychrolib.GetMoistAirDensity(TDryBulb=air_temperature, HumRatio=humidity_ratio, Pressure=atmospheric_pressure) # in kg m⁻³ [SI]

        self.forecast_preprocessed_df = pd.concat([self.forecast_preprocessed_df, density], axis=1)

    def forecast_preprocessing(self, route_df:pd.DataFrame, forecast_df:pd.DataFrame) -> pd.DataFrame:
        """
        TODO
        """
        self.route_df = route_df
        self.forecast_df = forecast_df

        self._cut_data()
        self._wind_log_correction()
        self._wind_decomposition()
        self._temperature_correction()
        self._air_density_estimation()

        return self.forecast_df
    
    def save_data(self):
        pass