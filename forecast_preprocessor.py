import pandas as pd
import math
import psychrolib # Psychrometric conversion library https://github.com/psychrometrics/psychrolib (Installation: https://pypi.org/project/PsychroLib/, Documentation: https://psychrometrics.github.io/psychrolib/api_docs.html)

class ForecastPreprocessor():

    def __init__(self) -> None:
        self.ROUGHNESS_LENGTH_Z0 = 0.03 # in meters from roughness class 1 (https://wind-data.ch/tools/profile.php?h=10&v=5&z0=0.03&abfrage=Refresh)
        self.REFERENCE_HEIGHT_H1 = 10.0 # in meters
        self.WIND_HEIGHT_H2 = 0.5 # in meters
        self.CORRECTING_FACTOR = math.log(self.WIND_HEIGHT_H2 / self.ROUGHNESS_LENGTH_Z0) / math.log(self.REFERENCE_HEIGHT_H1 / self.ROUGHNESS_LENGTH_Z0)

    def cut_data(self):
        pass

    def wind_log_correction(self):
        wind_vel2 = wind_vel1 * self.CORRECTING_FACTOR

    def wind_decomposition(self):
        pass

    def temperature_correction(self):
        if 8 < time < 20:
        # -2°C. during the night (20:00 - 08:00) +3°C
        elif 10 < time < 16:
        # during the day (10:00 - 16:00)
        else:
        # no correction in between.

    def air_density_estimation(self):
        """
        TODO https://wind-data.ch/tools/luftdichte.php?method=2&pr=990&t=25&rh=99&abfrage2=Aktualisieren
        """
        psychrolib.SetUnitSystem(psychrolib.SI)
        atmospheric_pressure = psychrolib.GetStandardAtmPressure(Altitude=altitude) # in Pa
        humidity_ratio = psychrolib.GetHumRatioFromRelHum(TDryBulb=tt, RelHum=rh/100, Pressure=atmospheric_pressure) # in kg_H₂O kg_Air⁻¹ [SI]
        density = psychrolib.GetMoistAirDensity(TDryBulb=tt, HumRatio=humidity_ratio, Pressure=atmospheric_pressure) # in kg m⁻³ [SI]

    def save_data(self):
        pass