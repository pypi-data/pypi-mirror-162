class InteractionsController(BaseController):


    def get_predefeined_interactions(self) -> List[str]:
    	pass

    async def play_predefined_interaction(self, inter_name: string, wait: boolean = False) -> None:
    	pass

    def interaction_running(self) -> boolean:
    	pass

    async def wait_interaction_finished(self) -> None:
    	pass

