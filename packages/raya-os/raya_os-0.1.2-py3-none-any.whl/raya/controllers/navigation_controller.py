class NavigationController(BaseController):


    async def get_list_of_maps(self):
    	pass

    async def get_status(self):
    	pass

    async def start_mapping(self, map_name: str = ''):
    	pass

    async def stop_mapping(self, save_map: bool = True):
    	pass

    async def get_map(self, map_name: str = ''):
    	pass

    async def set_map(self, map_name: str, wait_localization: bool = False, 
                      timeout: float = 0.0):
                      	pass

    async def is_localized(self):
    	pass

    async def wait_until_localized(self, timeout:float=0.0):
    	pass

    async def get_position(self, pos_unit: POS_UNIT = POS_UNIT.PIXEL, 
                     ang_unit: ANG_UNIT = ANG_UNIT.DEG):
                     	pass

    async def navigate_to_position(self, x: float, y: float, angle: float, 
                                    pos_unit: POS_UNIT = POS_UNIT.PIXEL, 
                                    ang_unit: ANG_UNIT = ANG_UNIT.DEG, 
                                    callback_feedback = None, 
                                    callback_finish = None, wait=False):
                                    	pass

    async def navigate_close_to_position(self, x: float, y: float,
                                         min_distance: float = 0.4,
                                         max_distance: float = 0.8,
                                         pos_unit: POS_UNIT = POS_UNIT.PIXEL, 
                                         callback_feedback = None, 
                                         callback_finish = None, wait=False):
                                         	pass

    async def navigate_to_zone(self, zone_name: str,
                               to_center: bool = True,
                               callback_feedback = None,
                               callback_finish = None,
                               wait=False):
                               	pass

    async def navigate_to_location(self, zone_name: str,
                                         to_center: bool = True,
                                         callback_feedback = None,
                                         callback_finish = None,
                                         wait=False):
                                         	pass

    async def cancel_navigation(self):
    	pass

    async def wait_navigation_finished(self):
    	pass

    async def save_location(self, location_name: str,
                             x: float, y: float, angle: float, 
                             pos_unit: POS_UNIT = POS_UNIT.PIXEL, 
                             ang_unit: ANG_UNIT = ANG_UNIT.DEG):
                             	pass

    async def save_zone(self, zone_name: str, points: list, 
                             pos_unit: POS_UNIT = POS_UNIT.PIXEL):
                             	pass

    async def get_zones(self, map_name:str = ''):
    	pass

    async def get_locations(self, map_name: str = ''):
    	pass

    async def get_zones_list(self, map_name: str = ''):
    	pass

    async def get_locations_list(self, map_name: str = ''):
    	pass

    async def delete_location(self, location_name: str, map_name: str = ''):
    	pass

    async def delete_zone(self, location_name: str, map_name: str = ''):
    	pass

    async def get_location(self, location_name: str,  
                             pos_unit: POS_UNIT = POS_UNIT.PIXEL):
                             	pass

    async def get_zone_center(self, zone_name: str,  
                             pos_unit: POS_UNIT = POS_UNIT.PIXEL):
                             	pass

    async def order_zone_points(self, zone_name: str,  
                             from_current_pose: bool = False):
                             	pass

    async def get_sorted_zone_point(self,  
                             pos_unit: POS_UNIT = POS_UNIT.PIXEL):
                             	pass

    async def is_in_zone(self, zone_name: str = ''):
    	pass

    def is_navigating(self):
    	pass

