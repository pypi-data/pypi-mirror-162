class SkillsController(BaseController):


    def get_available_skills(self) -> List[str]:
    	pass

    def get_skill_info(self, skill_name: str):
    	pass

    async def run_skill(self, skill_name: str, callback = None, wait=False, **kwargs) -> None:
    	pass

