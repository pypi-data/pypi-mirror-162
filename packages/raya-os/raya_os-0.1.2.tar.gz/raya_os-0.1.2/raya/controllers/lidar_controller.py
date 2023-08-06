class LidarController(BaseController):


    def get_laser_info(self, ang_unit: ANG_UNIT = ANG_UNIT.DEG) -> dict:
    	pass

    def get_raw_data(self):
    	pass

    def check_obstacle(self,
                       lower_angle: float,
                       upper_angle: float,
                       lower_distance: float = 0.0,
                       upper_distance: float = float('inf'),
                       ang_unit: ANG_UNIT = ANG_UNIT.DEG) -> bool:
    	pass

    def create_obstacle_listener(self, listener_name: str,
                          callback: callable,
                          lower_angle: float,
                          upper_angle: float,
                          lower_distance: float = 0.0,
                          upper_distance: float = float('inf'),
                          ang_unit: ANG_UNIT = ANG_UNIT.DEG) -> None:
    	pass

