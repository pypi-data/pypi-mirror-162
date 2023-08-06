class ArmsController(BaseController):


    def get_list_of_arms(self):
    	pass

    def get_state_of_arm(self, arm: str):
    	pass

    def get_limits_of_joints(self, arm: str, units: ANG_UNIT = ANG_UNIT.DEG):
    	pass

    def get_list_predefined_poses(self, arm: str):
    	pass

    def is_gripper_in_execution(self, arm: str):
    	pass

    def is_arm_in_execution(self, arm: str):
    	pass

    def are_checkings_in_progress(self):
    	pass

    async def set_pose(
        self,
        arm: str,
        x: float,
        y: float,
        z: float,
        roll: float,
        pitch: float,
        yaw: float,
        units: ANG_UNIT = ANG_UNIT.DEG,
        cartesian_path: bool = False,
        tilt_constraint: bool = False,
        callback_feedback=None,
        callback_finish=None,
        wait=False,
    ):
    	pass

    async def set_pose_q(
        self,
        arm: str,
        x: float,
        y: float,
        z: float,
        qx: float,
        qy: float,
        qz: float,
        qw: float,
        cartesian_path: bool = False,
        tilt_constraint: bool = False,
        callback_feedback=None,
        callback_finish=None,
        wait=False,
    ):
    	pass

    async def set_predefined_pose(
        self,
        arm: str,
        predefined_pose: str,
        tilt_constraint: bool = False,
        callback_feedback=None,
        callback_finish=None,
        wait=False,
    ):
    	pass

    async def set_joints_position(
        self,
        arm: str,
        name_joints: list,
        angle_joints: list,
        units: ANG_UNIT = ANG_UNIT.DEG,
        tilt_constraint: bool = False,
        callback_feedback=None,
        callback_finish=None,
        wait=False,
    ):
    	pass

    async def is_pose_valid(
        self,
        arm: str,
        x: float,
        y: float,
        z: float,
        roll: float,
        pitch: float,
        yaw: float,
        units: ANG_UNIT = ANG_UNIT.DEG,
        callback_finish=None,
        wait=False,
    ):
    	pass

    async def is_pose_valid_q(
        self,
        arm: str,
        x: float,
        y: float,
        z: float,
        qx: float,
        qy: float,
        qz: float,
        qw: float,
        callback_finish=None,
        wait=False,
    ):
    	pass

    async def are_joints_position_valid(
        self,
        arm: str,
        name_joints: list,
        angle_joints: list,
        units: ANG_UNIT = ANG_UNIT.DEG,
        callback_finish=None,
        wait=False,
    ):
    	pass

    async def set_gripper_open(
        self,
        arm: str,
        callback_finish=None,
        wait=False,
    ):
    	pass

    async def set_gripper_close(
        self,
        arm: str,
        desired_pressure: float = 10.0,
        width: float = 0.0,
        callback_finish=None,
        wait=False,
    ):
    	pass

