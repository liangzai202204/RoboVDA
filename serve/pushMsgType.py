from typing import List, Dict,Optional
from pydantic import BaseModel


class Lock(BaseModel):
    desc: str = ""
    ip: str = ""
    locked: bool
    nick_name: str = ""
    port: int = 0
    ret_code: int = 0
    time_t: int = 0
    type: int = 0


class Motor(BaseModel):
    calib: bool = False
    can_id: int = 0
    can_router: int = 0
    current: int = 0
    emc: bool = False
    encoder: int = 0
    err: bool = False
    error_code: int = 0
    follow_err: bool = False
    motor_name: str = ""
    passive: bool = False
    position: int = 0
    raw_position: int = 0
    speed: int = 0
    stop: bool = False
    temperature: int = 0
    type: int = 0
    voltage: int = 0


class Joint(BaseModel):
    angle: int = 0
    current: int = 0
    temperature: int = 0
    type: str = ""
    velocity: int = 0
    voltage: int = 0


class ArmInfo(BaseModel):
    endpos: Dict[str, int] = {}
    joints: List[Joint] = []
    task_status: int = 0


class Fork(BaseModel):
    fork_auto_flag: bool = False
    fork_height: float = 0.0
    fork_height_in_place: bool = False
    fork_pressure_actual: float = 0.0
    forward_in_place: bool = False
    forward_val: float = 0.0


class Hook(BaseModel):
    hook_angle: int = 0
    hook_clamping_state: bool = False
    hook_emc: bool = False
    hook_enable: bool = False
    hook_error_code: int = 0
    hook_height: int = 0
    hook_isFull: bool = False
    hook_mode: bool = False
    hook_state: int = 0


class Jack(BaseModel):
    jack_emc: bool = False
    jack_enable: bool = False
    jack_error_code: int = 0
    jack_height: float = 0.0
    jack_isFull: bool = False
    jack_load_times: int = 0
    jack_mode: bool = False
    jack_speed: int = 0
    jack_state: int = 0


class DIs(BaseModel):
    id: int = 0
    status: bool = False


class DOs(BaseModel):
    id: int = 0
    status: bool = False


class TaskStatus(BaseModel):
    status: int = 0
    task_id: str = ""
    type: int = 0


class TaskStatusPackage(BaseModel):
    closest_label: str = ""
    closest_target: str = ""
    distance: int = 0
    info: str = ""
    percentage: int = 0
    source_label: str = ""
    source_name: str = ""
    target_label: str = ""
    target_name: str = ""
    task_status_list: List[TaskStatus] = []


class TasklistStatus(BaseModel):
    actionGroupId: int = 0
    actionIds: Optional[List[int]] = []
    loop: bool = False
    taskId: int = 0
    taskListName: str = ""
    taskListStatus: int = 0



class RobotPush(BaseModel):
    DI: List[DIs] = []
    DO: List[DOs] = []
    acc_x: float = 0.
    acc_y: float = 0.
    acc_z: float = 0.
    angle: float = 0.
    ap_addr: str = ''
    area_ids: List[str] = []
    arm_info: ArmInfo = ArmInfo()
    auto_charge: bool = False
    battery_cycle: int = 0
    battery_level: float = 0.
    battery_temp: float = 0.
    battery_user_data: str = ''
    block_x: float = 0.
    block_y: float = 0.
    blocked: bool = False
    brake: bool = False
    charging: bool = False
    confidence: float = 0.
    controller_humi: float = 0.
    controller_temp: float = 0.
    controller_voltage: float = 0.
    correction_errs: List[int] = []
    create_on: str = ''
    current: float = 0.
    current_lock: Optional[Lock] = None
    current_map: str = ''
    current_map_md5: str = ''
    current_station: str = ''
    detect_skid: bool = False
    di_max_node: int = 0
    dispatch_mode: int = 0
    do_max_node: int = 0
    driver_emc: bool = False
    dsp_version: str = ''
    electric: bool = False
    emergency: bool = False
    errors: List[dict] = []
    fatals: List[dict] = []
    warnings: List[dict] = []
    notices: List[dict] = []
    finished_path: List[str] = []
    fork: Fork = Fork()
    gyro_version: str = ''
    hook: Hook = Hook()
    imu_header: Dict[str, str] = {}
    in_forbidden_area: bool = False
    is_stop: bool = False
    jack: Jack = Jack()
    loadmap_status: int = 0
    loc_state: int = 0
    manual_charge: bool = False
    model: str = ''
    motor_info: List[Motor] = []
    motor_steer_angles: List[int] = []
    move_status_info: str = ''
    nearest_obstacles: List[str] = []
    odo: float = 0.
    peripheral_data: List[str] = []
    pgvs: List[str] = []
    pitch: float = 0.
    qw: float = 0.
    qx: float = 0.
    qy: float = 0.
    qz: float = 0.
    r_spin: float = 0.
    r_steer: float = 0.
    r_steer_angles: List[float] = []
    r_vx: float = 0.
    r_vy: float = 0.
    r_w: float = 0.
    reliabilities: List[str] = []
    reloc_status: int = 0
    requestCurrent: float = 0.
    requestVoltage: float = 0.
    ret_code: int = 0
    rfids: List[str] = []
    robot_note: str = ''
    roll: float = 0.
    roller: Dict[str, int] = {}
    rot_off_x: int = 0
    rot_off_y: int = 0
    rot_off_z: int = 0
    rot_x: float = 0.
    rot_y: float = 0.
    rot_z: float = 0.
    rssi: int = 0
    running_status: int = 0
    similarity: int = 0
    slam_status: int = 0
    slowed: bool = False
    soft_emc: bool = False
    spin: float = 0.
    src_release: bool = False
    ssid: str = ''
    steer: float = 0.
    steer_angles: List[float] = []
    target_dist: float = 0.
    target_id: str = ''
    target_label: str = ''
    target_point: List[float] = []
    target_x: float = 0.
    target_y: float = 0.
    task_status: int = 0
    task_status_package: TaskStatusPackage = TaskStatusPackage()
    task_type: int = 0
    tasklist_status: TasklistStatus = TasklistStatus()
    time: int = 0
    today_odo: float = 0.
    total_time: int = 0
    tracking_status: int = 0
    transparent_data: Dict[str, str] = {}
    unfinished_path: List[str] = []
    update_reason: int = 0
    user_objects: List[str] = []
    vehicle_id: str = ''
    version: str = ''
    voltage: float = 0.
    vx: float = 0.
    vy: float = 0.
    w: float = 0.
    x: float = 0.
    y: float = 0.
    yaw: float = 0.



class RobotReq(BaseModel):
    # robot_status_current_lock
    robotStatusCurrentLock: Optional[Lock]



