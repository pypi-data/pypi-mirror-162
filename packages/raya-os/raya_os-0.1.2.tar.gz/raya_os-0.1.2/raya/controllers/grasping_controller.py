class GraspingController(BaseController):


    async def pick_object(self, detector_model: string, object_name: string, 
                          source: string, arms:list = [], callback_feedback = None, 
                          callback_finish = None, wait=False):
                          	pass

    async def place_object_with_reference(self, detector_model:str, source:str, 
            object_name:str, height_object:float, distance:float,  arm: str,
            callback_feedback = None, callback_finish = None, wait=False):
            	pass

    async def place_object_with_point(self, point_to_place:list,
            height_object:float, arm:str, callback_feedback = None, 
            callback_finish = None, wait=False):
            	pass

    async def cancel_grasping(self):
    	pass

    async def wait_grasping_finished(self):
    	pass

    def is_grasping(self):
    	pass

