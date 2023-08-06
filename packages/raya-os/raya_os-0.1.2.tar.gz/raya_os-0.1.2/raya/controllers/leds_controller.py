class LedsController(BaseController):


    def get_groups(self)-> List[str]:
    	pass

    def get_colors(self, group: string) -> List[str]:
    	pass

    def get_animations(self, group: string) -> List[str]:
    	pass

    def get_max_speed(self, group: string) -> List[str]:
    	pass

    async def animation(self, group: string, color: string, animation: string, 
                        speed: int = 1, repetitions: int = 1) -> None:
    	pass

