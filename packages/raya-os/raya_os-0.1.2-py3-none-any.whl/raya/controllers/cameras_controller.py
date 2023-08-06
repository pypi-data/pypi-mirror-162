class CamerasController(BaseController):


    def available_color_cameras(self):
    	pass

    async def enable_color_camera(self, camera_name: str):
    	pass

    def disable_color_camera(self, camera_name: str):
    	pass

    async def check(self, ofir: str, compressed=False):
    	pass

    def create_color_frame_listener(self, *, camera_name:str, 
                                             callback,  
                                             compressed:bool=False):
                                             	pass

    def delete_listener(self, camera_name):
    	pass

