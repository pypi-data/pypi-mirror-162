class DetectionObjectsHandler:


    def get_objects_names(self):
    	pass

    def get_current_detections(self):
    	pass

    async def find_objects(self, objects:list, callback = None, 
                           wait:bool = False, timeout:float = 0.0):
                           	pass

    def cancel_find_objects(self):
    	pass

class DetectionTagsHandler:


    def get_current_detections(self):
    	pass

    async def find_tags(self, tags:dict, callback = None, wait = False, timeout = 0.0):
    	pass

    def cancel_find_tags(self):
    	pass

class DetectionFacesHandler:


    def get_current_detections(self):
    	pass

class RecognitionFacesHandler:


    def get_faces_names(self):
    	pass

    def get_current_recognitions(self):
    	pass

class CVController(BaseController):


    def get_available_models(self):
    	pass

    async def enable_model(self, model:str, type:str, name:str, source:str, 
                        model_params:dict = {}):  
                        	pass

    async def disable_model(self, model:str, type:str):
    	pass

