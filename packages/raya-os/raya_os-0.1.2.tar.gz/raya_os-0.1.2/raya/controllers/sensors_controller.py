class SensorsController(BaseController):


    def get_all_sensors_values(self):
    	pass

    def get_sensor_value(self, sensor_path: str):
    	pass

    def check_sensor_in_range(self, sensor_path: str, 
                                    lower_bound: float = float('-inf'),
                                    higher_bound: float = float('inf'), 
                                    inside_range: bool = True, 
                                    abs_val: bool = False):
                                    	pass

    def create_threshold_listener(self, *, listener_name: str, 
                                           callback,
                                           sensors_paths, 
                                           lower_bound: float = float('-inf'),
                                           higher_bound: float = float('inf'), 
                                           inside_range: bool = True, 
                                           abs_val: bool = False):
                                           	pass

    def create_boolean_listener(self, *, listener_name: str, 
                                         callback,
                                         sensors_paths, 
                                         logic_state: bool):
                                         	pass

