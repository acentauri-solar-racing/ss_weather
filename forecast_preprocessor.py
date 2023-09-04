import pandas as pd
import math
import psychrolib # Psychrometric conversion library https://github.com/psychrometrics/psychrolib (Installation: https://pypi.org/project/PsychroLib/, Documentation: https://psychrometrics.github.io/psychrolib/api_docs.html)

class ForecastPreprocessor():
    """
    TODO
    """

    def __init__(self) -> None:
        self.ROUGHNESS_LENGTH_Z0 = 0.03 # in meters from roughness class 1 (https://wind-data.ch/tools/profile.php?h=10&v=5&z0=0.03&abfrage=Refresh)
        self.REFERENCE_HEIGHT_H1 = 10.0 # in meters
        self.WIND_HEIGHT_H2 = 0.5 # in meters
        self.CORRECTING_FACTOR = math.log(self.WIND_HEIGHT_H2 / self.ROUGHNESS_LENGTH_Z0) / math.log(self.REFERENCE_HEIGHT_H1 / self.ROUGHNESS_LENGTH_Z0)

        self.route_df : pd.DataFrame = pd.DataFrame()
        self.processing_df : pd.DataFrame = pd.DataFrame()

    def _data_cut_time(self, hours_in_advance:int, print_is_requested:bool=False) -> None:
        """
        TODO
        """
        # Drop past columns: less than now
        now = pd.Timestamp.now()
        self.processing_df = self.processing_df[self.processing_df.index.get_level_values('time') >= now]
        
        # Drop future columns: more than x hours
        self.processing_df = self.processing_df[self.processing_df.index.get_level_values('time') <= now + pd.Timedelta(hours=hours_in_advance)]

        if print_is_requested:
            print(f'Forecast data cut to {hours_in_advance} hours in advance. \n {self.processing_df}')

    def _temperature_correction(self, print_is_requested:bool=False) -> None:
        """
        Corrections suggested by Pascal Graf from Meteotest.
        """
        # Extract the time values from the multi-index
        times_hours = self.processing_df.index.get_level_values('time').hour

        # Apply corrections based on the time
        mask_night = (times_hours >= 20) | (times_hours <= 8)
        mask_day = (times_hours >= 10) & (times_hours <= 16)

        # Change column name
        self.processing_df.rename(columns={'tt': 'temperature'}, inplace=True)

        # Apply the corrections
        self.processing_df.loc[mask_night, 'temperature'] -= 2 # Subtract 2°C during the night
        self.processing_df.loc[mask_day, 'temperature'] += 3 # Add 3°C during the day
        # No correction is applied for the in-between times as they remain unchanged

        if print_is_requested:
            print(f'Temperature correction applied. \n {self.processing_df}')

    def _wind_log_correction(self, print_is_requested:bool=False) -> None:
        """
        Correct the wind speed forecast at 10 meters to the wind speed at 0.5 meters.
        Equation taken from: https://wind-data.ch/tools/profile.php?h=10&v=5&z0=0.03&abfrage=Refresh
        """
        self.processing_df.rename(columns={'ff': 'windSpeed'}, inplace=True)
        self.processing_df *= self.CORRECTING_FACTOR / 3.6 # Convert from km/h to m/s

        if print_is_requested:
            print(f'Wind log correction applied. \n {self.processing_df}')

    def _wind_decomposition(self, print_is_requested:bool=False) -> None:
        """
        TODO
        """
        # Extract relevant angles
        theta = self.route_df['theta'] # in degrees
        wind_direction = self.processing_df['dd'] # in degrees
        attack_angle = wind_direction - theta # in degrees

        # Calculate wind speed components
        wind_speed_side = pd.DataFrame(self.processing_df['windSpeed'] * math.sin(math.radians(attack_angle)) / 3.6, columns=['sideWind']) # in m/s
        wind_speed_front = pd.DataFrame(self.processing_df['windSpeed'] * math.cos(math.radians(attack_angle)) / 3.6, columns=['frontWind']) # in m/s

        self.processing_df = pd.concat([self.processing_df, wind_speed_side, wind_speed_front], axis=1)

        if print_is_requested:
            print(f'Wind decomposition applied. \n {self.processing_df}')

    def _air_density_estimation(self, print_is_requested:bool=False) -> None:
        """
        TODO https://wind-data.ch/tools/luftdichte.php?method=2&pr=990&t=25&rh=99&abfrage2=Aktualisieren
        """
        psychrolib.SetUnitSystem(psychrolib.SI)

        # Extract altitude data and calculate atmospheric pressure
        altitude = self.route_df['altitudeSmoothed'] # in meters
        atmospheric_pressure = psychrolib.GetStandardAtmPressure(Altitude=altitude) # in Pa

        # Extract temperature and relative humidity data and calculate humidity ratio
        air_temperature = self.processing_df['temperature'] # in °C
        relative_humidity = self.processing_df['rh'] # in %
        humidity_ratio = psychrolib.GetHumRatioFromRelHum(TDryBulb=air_temperature, RelHum=relative_humidity/100, Pressure=atmospheric_pressure) # in kg_H₂O kg_Air⁻¹ [SI]

        # Calculate air density
        density = psychrolib.GetMoistAirDensity(TDryBulb=air_temperature, HumRatio=humidity_ratio, Pressure=atmospheric_pressure) # in kg m⁻³ [SI]

        density_df = pd.DataFrame(density, columns=['airDensity'])
        self.processing_df = pd.concat([self.processing_df, density_df], axis=1)

        if print_is_requested:
            print(f'Air density estimation applied. \n {self.processing_df}')

    def forecast_preprocessing(self, route_df:pd.DataFrame, forecast_df:pd.DataFrame, hours_in_advance:int, print_is_requested:bool=False) -> pd.DataFrame:
        """
        TODO
        """
        # Save the dataframes
        self.route_df = route_df

        # Distinguish between the two forecast products
        if len(forecast_df.columns) < 10:
            # CloudMove
            column_name = ['tt', 'gh']
            self.processing_df = forecast_df[column_name]

            self._data_cut_time(hours_in_advance, print_is_requested=print_is_requested)
            self._temperature_correction(print_is_requested=print_is_requested)

        else:
            # SolarForecast
            column_name = ['tt', 'gh', 'rh', 'ff', 'dd', 'fx']
            self.processing_df = forecast_df[column_name]

            self._data_cut_time(hours_in_advance, print_is_requested=print_is_requested)
            self._temperature_correction(print_is_requested=print_is_requested)
            self._wind_log_correction(print_is_requested=print_is_requested)
            self._wind_decomposition(print_is_requested=print_is_requested)
            self._air_density_estimation(print_is_requested=print_is_requested)

        return self.processing_df
    
    def save_data(self):
        """
        TODO
        """
        pass