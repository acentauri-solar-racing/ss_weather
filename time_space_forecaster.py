import functions
import pandas as pd
from route import Route
from gps import GPS
from db_querier import DbQuerier
from optimal_reader import OptimalReader


class TimeSpaceForecaster():
    """ """
    
    def __init__(self, route:Route, gps:GPS, db_querier:DbQuerier, optimal_reader:OptimalReader) -> None:
        self.route = route
        self.gps = gps
        self.db_querier = db_querier
        self.opt_reader = optimal_reader

        self.route_data = self.route.get_route_data
        self.control_stops = self.route.get_control_stops_data

        self.current_cumDistance: float = 0.0

        self.working_df = pd.DataFrame()
        self.working_col_name = ''
    
    def _cum_time_at_input_velocity(self, velocity:float) -> None:
        """ vel in km/h """
        time_at_input_v = self.route_data['distance'] / velocity * 3.6

        self.working_col_name = 'cumTimeAtInputVelocity'
        self.working_df = self.route_data.copy()
        self.working_df[self.working_col_name] = time_at_input_v.cumsum()
    
    def _recursive_position_finder(self, driving_time:float, cs_to_skip:int, print_is_requested:bool=False) -> pd.Series:
        """ """
        # Cut data at current position (lower cut)
        cut_data = self.working_df.copy()

        cut_data = cut_data[cut_data['cumDistance'] >= self.current_cumDistance]
        cut_data = cut_data.reset_index(drop=True)

        current_time = cut_data[self.working_col_name][0]

        # Cut data at driving time (upper cut)
        cut_data = cut_data[cut_data[self.working_col_name] <= current_time + driving_time]
        max_cumDistance = cut_data['cumDistance'].max()

        # Check if the control stop dataframe is not empty
        if not self.control_stops.empty:
            cs_in_range_mask = (self.control_stops['cumDistance'] >= self.current_cumDistance) & (self.control_stops['cumDistance'] <= max_cumDistance)
            cs_in_range = cs_in_range_mask.sum()

            if print_is_requested:
                print(f'cs found ahead: {cs_in_range}')
                print(f'cs to skip: {cs_to_skip}')
        else:
            print("No control stop dataframe given")

        # Stop cases
        # Reach end of route, return last point
        if self.current_cumDistance >= self.route_data.iloc[-1]['cumDistance']:
            return self.route_data.iloc[-1] # return self.end_position
        
        # All control stops considered
        if cs_to_skip == cs_in_range:
            print("All control stops considered")
            return self.route_data.loc[self.route_data['cumDistance'] == max_cumDistance].iloc[0]
        
        # Stop at control stop for the night, meaning we arrive at cs between 16:30 and 17:00
        if cs_to_skip > cs_in_range:
            print("Stop at control stop for the night")
            return self.control_stops.loc[self.control_stops['cumDistance'] > self.current_cumDistance].iloc[cs_to_skip - 1]
        

        # Recursive call to skip control stop and reduce driving time by 30 minutes (passed in seconds)
        if cs_to_skip < cs_in_range: # Case of 0 cs in range considered
            print("--- Recursive call ---")
            return self._recursive_position_finder(driving_time - 30.0*60.0, cs_to_skip + 1)
    
    def get_cum_distance_forecast(self, current_position:dict, type:str, time:dict={'hour': 17, 'minute': 0}, speed:float=60) -> float:
        """ """
        # Save current cumulative distance
        self.current_cumDistance = current_position['cumDistance']

        # Subtract start time to now
        now_race = functions.get_race_time()
        driving_time = pd.Timedelta(hours=time['hour'], minutes=time['minute']) - pd.Timedelta(hours=now_race.hour, minutes=now_race.minute)

        # Check if the driving time is positive
        if driving_time.total_seconds() < 0:
            raise ValueError(f"Driving time is negative: {driving_time.total_seconds()}")

        if "max_speed" in type:
            # Set working dataframe
            self.working_df = self.route_data.copy()
            self.working_col_name = 'cumTimeAtMaxSpeedLim'

        elif "mean_speed_cruise" in type:
            # Call the db querier
            mean_velocity = self.db_querier.get_day_mean_velocity60

            # Set working dataframe
            self._cum_time_at_input_velocity(mean_velocity)

        elif "mean_speed" in type:
            # Call the db querier
            mean_velocity = self.db_querier.get_day_mean_velocity

            # Set working dataframe
            self._cum_time_at_input_velocity(mean_velocity)

        elif "optimal_speed" in type:
            # Call the opt reader
            opt_velocity = self.opt_reader.get_mean_velocity #TODO IMPROVE OPTIMIZED VELOCITY

            # Set working dataframe
            self._cum_time_at_input_velocity(opt_velocity)

        else:
            if speed is not None:
                self._cum_time_at_input_velocity(speed)
            else:
                raise ValueError(f"type must be 'max_speed', 'mean_speed_cruise', 'mean_speed' or 'opt_speed'. Received: {type} \n speed has to be given if type is not given")
        
        # Call the recursive finder
        position_series = self._recursive_position_finder(driving_time.total_seconds(), cs_to_skip=0)

        return position_series['cumDistance']
    
    def get_time_at_next_control_stop(self, current_position:dict, type:str, speed:float=60) -> pd.Timestamp:
        """ """
        next_cs, _ = self.route.find_next_cs(current_position)
        row, _ = self.route.find_closest_row(current_position)

        current_cumDistance = row['cumDistance']

        delta_m = next_cs['cumDistance'] - current_cumDistance

        now_race = functions.get_race_time()

        if "max_speed" in type:
            current_time = row['cumTimeAtMaxSpeedLim']
            cs_time = next_cs['cumTimeAtMaxSpeedLim']

            delta_sec = cs_time - current_time

            return now_race + pd.Timedelta(seconds=delta_sec)

        elif "mean_speed_cruise" in type:
            # Call the db querier
            mean_velocity = self.db_querier.get_day_mean_velocity60
            delta_h = (delta_m / 1000) / mean_velocity

            return now_race + pd.Timedelta(hours=delta_h)

        elif "mean_speed" in type:
            # Call the db querier
            mean_velocity = self.db_querier.get_day_mean_velocity
            delta_h = (delta_m / 1000) / mean_velocity

            return now_race + pd.Timedelta(hours=delta_h)

        elif "optimal_speed" in type:
            # Call the opt reader
            opt_velocity = self.opt_reader.get_mean_velocity #TODO IMPROVE OPTIMIZED VELOCITY
            delta_h = (delta_m / 1000) / opt_velocity

            return now_race + pd.Timedelta(hours=delta_h)

        else:
            if speed is not None:
                delta_h = (delta_m / 1000) / speed

                return now_race + pd.Timedelta(hours=delta_h)
            else:
                raise ValueError(f"type must be 'max_speed', 'mean_speed_cruise', 'mean_speed' or 'opt_speed'. Received: {type} \n speed has to be given if type is not given")
        