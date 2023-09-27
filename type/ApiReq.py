import enum


class ApiReq(enum.Enum):
    ROBOT_CONFIG_DOWNLOADMAP_REQ = 4011
    ROBOT_STATUS_MAPMD5_REQ = 1302  # 获取指定地图列表的md5
    ROBOT_CONTROL_LOADMAP_REQ = 2022
    ROBOT_STATUS_MAP_REQ = 1300
    ROBOT_CONFIG_LOCK_REQ = 4005
    ROBOT_TASK_CANCEL_REQ = 3003
    ROBOT_TASK_GO_TARGET_REQ = 3051
    ROBOT_TASK_GOTARGETLIST_REQ = 3066
    ROBOT_TASK_CLEARTARGETLIST_REQ = 3067
    ROBOT_CONTROL_RELOC_REQ = 2002
    ROBOT_STATUS_TASK_STATUS_PACKAGE_REQ = 1110
    ROBOT_PUSH_CONFIG_REQ = 9300  # 19301 端口配置
    ROBOT_STATUS_MODEL_REQ = 1500  # 下载模型文件
    ROBOT_TASK_PAUSE_REQ = 3001  # 暂停导航
    ROBOT_TASK_RESUME_REQ = 3002  # 继续导航

