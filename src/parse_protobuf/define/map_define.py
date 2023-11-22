from src.parse_protobuf.define.gnss_define import Message_GNSS, Message_AllGNSS
from src.parse_protobuf.define.header_define import Message_Header
from src.parse_protobuf.define.imu_define import Message_IMU
from src.parse_protobuf.define.localization_define import Message_Localization
from src.parse_protobuf.define.model_define import Message_Device
# message Message_MapLogData {
#     double robot_odo_x = 1;
#     double robot_odo_y = 2;
#     double robot_odo_w = 3;
#     repeated double laser_beam_dist = 4;
#     repeated double laser_beam_angle = 5;
#     repeated double rssi = 6;
#     Message_Header header = 7;
# }


class Message_MapLogData:
    robot_odo_x: float
    robot_odo_y: float
    robot_odo_w: float
    laser_beam_dist: list[float]
    laser_beam_angle: list[float]
    rssi: list[float]
    header: Message_Header

# message Message_MapOdo {
#     double timestamp = 1;
#     float odo_x = 2;
#     float odo_y = 3;
#     float odo_w = 4;
#     float odo_vx = 5;
#     float odo_vy = 6;
#     float odo_vw = 7;
# }
class Message_MapOdo:
    timestamp: float
    odo_x: float
    odo_y: float
    odo_w: float
    odo_vx: float
    odo_vy: float
    odo_vw: float

# message Message_MapLogData3D {
#     double timestamp = 1;
#     repeated float x = 2;
#     repeated float y = 3;
#     repeated float z = 4;
#     repeated uint32 intensity = 5;
#     repeated uint32 timeoffset = 6;
#     repeated uint32 ring = 7;
#     repeated bytes data = 8;
#     repeated float firstAzimuth = 9;
#     repeated float secondAzimuth = 10;
# }
class Message_MapLogData3D:
    timestamp: float
    x: list[float]
    y: list[float]
    z: list[float]
    intensity: list[int]
    timeoffset: list[int]
    ring: list[int]
    data: list[bytes]
    firstAzimuth: list[float]
    secondAzimuth: list[float]
# message Message_MapLog {
#     double laser_pos_x = 1;
#     double laser_pos_y = 2;
#     double laser_pos_z = 3;//由于版本原因里面设置是激光安装yaw角，取激光高度数据从laser_install_height
#     double laser_step = 4;
#     double laser_range_max = 5;
#     repeated Message_MapLogData log_data = 6;
#     string laser_name = 7;
#     double laser_install_height = 8;
#     repeated Message_MapOdo odometer = 9;
#     repeated Message_MapLogData3D log_data3d = 10;
#     double laser_install_yaw = 11;
#     double laser_install_pitch = 12;
#     double laser_install_roll = 13;
#     repeated Message_IMU imu_data = 14;
#     repeated Message_GNSS gnss_data = 15;
#     uint32 lasertype = 16; // lasertype = 1---robosense 16  lasertype = 2----robosense helios   lasertype = 3----velodyne 16
#     float factor = 17;
#     repeated float azimuthcorrection = 18;
#     repeated float verticalcorrection = 19;
#     repeated Message_AllGNSS all_gnss_data = 20; // 支持多个天线设备
# }
class Message_MapLog:
    laser_pos_x: float
    laser_pos_y: float
    laser_pos_z: float
    laser_step: float
    laser_range_max: float
    log_data: list[Message_MapLogData]
    laser_name: str
    laser_install_height: float
    odometer: list[Message_MapOdo]
    log_data3d: list[Message_MapLogData3D]
    laser_install_yaw: float
    laser_install_pitch: float
    laser_install_roll: float
    imu_data: list[Message_IMU]
    gnss_data: list[Message_GNSS]
    lasertype: int
    factor: float
    azimuthcorrection: list[float]
    verticalcorrection: list[float]
    all_gnss_data: list[Message_AllGNSS]

# message Message_LocalMapLog {
#     double laser_pos_x = 1;
#     double laser_pos_y = 2;
#     double laser_pos_z = 3;//由于版本原因里面设置是激光安装yaw角，取激光高度数据从laser_install_height
#     double laser_step = 4;
#     double laser_range_max = 5;
#     repeated Message_MapLogData log_data = 6;
#     string laser_name = 7;
#     double laser_install_height = 8;
#     repeated Message_MapOdo odometer = 9;
#     repeated Message_MapLogData3D log_data3d = 10;
#     double laser_install_yaw = 11;
#     double laser_install_pitch = 12;
#     double laser_install_roll = 13;
#     repeated Message_IMU imu_data = 14;
#     repeated Message_GNSS gnss_data = 15;
#     uint32 lasertype = 16; // lasertype = 1---robosense 16  lasertype = 2----robosense helios   lasertype = 3----velodyne 16
#     float factor = 17;
#     repeated float azimuthcorrection = 18;
#     repeated float verticalcorrection = 19;
#     repeated Message_Localization localization_data = 20;
# }


class Message_LocalMapLog:
    laser_pos_x: float
    laser_pos_y: float
    laser_pos_z: float
    laser_step: float
    laser_range_max: float
    log_data: list[Message_MapLogData]
    laser_name: str
    laser_install_height: float
    odometer: list[Message_MapOdo]
    log_data3d: list[Message_MapLogData3D]
    laser_install_yaw: float
    laser_install_pitch: float
    laser_install_roll: float
    imu_data: list[Message_IMU]
    gnss_data: list[Message_GNSS]
    lasertype: int
    factor: float
    azimuthcorrection: list[float]
    verticalcorrection: list[float]
    localization_data: list[Message_Localization]


# message Message_MapProperty {
#     string key = 1;
#     string type = 2; //如果type = "json"时,表示 string_value中是个json的string 方便以后扩展
#     bytes value = 3; // for backward compatibility
#     oneof oneof_value {
#         string string_value = 4;
#         bool bool_value = 5;
#         int32 int32_value = 6;
#         uint32 uint32_value = 7;
#         int64 int64_value = 8;
#         uint64 uint64_value = 9;
#         float float_value = 10;
#         double double_value = 11;
#         bytes bytes_value = 12;
#     }
#     string tag = 13; //调度场景专用表示该key作用于指定机器人组(例如: "group:test_1,group1:test_2,group2")如果为空表示作用于所有机器人
# }
class Message_MapProperty:
    key: str
    type: str
    value: bytes
    string_value: str
    bool_value: bool
    int32_value: int
    uint32_value: int
    int64_value: int
    uint64_value: int
    float_value: float
    double_value: float
    bytes_value: bytes
    tag: str

# message Message_MapPos {
#     double x = 1;
#     double y = 2;
#     double z = 3;
# }
class Message_MapPos:
    x: float
    y: float
    z: float

# message Message_MapRSSIPos {
#     double x = 1;
#     double y = 2;
# }
class Message_MapRSSIPos:
    x: float
    y: float
# message Message_ReflectorPos {
#     string type = 1;
#     double width = 2;
#     double x = 3;
#     double y = 4;
# }

class Message_ReflectorPos:
    type: str
    width: float
    x: float
    y: float

# message Message_LiveRefPos {
#     repeated Message_ReflectorPos ref_pos = 1;
# }
class Message_LiveRefPos:
    ref_pos: list[Message_ReflectorPos]
# message Message_tagPos {
#     uint32 tag_value = 1;
#     double x = 2 ;
#     double y = 3;
#     double angle = 4 ;
#     bool is_DMT_detected = 5;
#     double z = 6;
#     double qx = 7;
#     double qy = 8;
#     double qz = 9;
#     double qw = 10;
#     double variance = 11;
#     string class_name = 12;  //2DTAG,3DTAG
#     repeated Message_MapProperty property = 13;
# }
class Message_tagPos:
    tag_value: int
    x: float
    y: float
    angle: float
    is_DMT_detected: bool
    z: float
    qx: float
    qy: float
    qz: float
    qw: float
    variance: float
    class_name: str
    property: list[Message_MapProperty]

# message Message_MapLine {
#     Message_MapPos start_pos = 1;
#     Message_MapPos end_pos = 2;
# }
class Message_MapLine:
    start_pos: Message_MapPos
    end_pos: Message_MapPos

# message Message_MapHeader {
#     string map_type = 1;    //type of map: 2D-Map or 3D-Map
#     string map_name = 2;    //name of map: the map file name
#     Message_MapPos min_pos = 3;
#     Message_MapPos max_pos = 4;
#     double resolution = 5; //unit: m
#     string version = 8;
# }
class Message_MapHeader:
    map_type: str
    map_name: str
    min_pos: Message_MapPos
    max_pos: Message_MapPos
    resolution: float
    version: str

# message Message_MapAttribute {
#     string description = 1; // description of the this class
#     uint32 color_pen = 2;
#     uint32 color_brush = 3;
#     uint32 color_font = 4;
# }
class Message_MapAttribute:
    description: str
    color_pen: int
    color_brush: int
    color_font: int

# message Message_AdvancedPoint {
#     string class_name = 1;    //the class_name from the Message_AdvancedObjectDefine
#     string instance_name = 2; // the name of this instance
#     Message_MapPos pos = 3;
#     double dir = 4;
#     repeated Message_MapProperty property = 5; // write in json
#     bool ignore_dir = 6;
#     bytes desc = 8;
#     Message_MapAttribute attribute = 10;
# }
class Message_AdvancedPoint:
    class_name: str
    instance_name: str
    pos: Message_MapPos
    dir: float
    property: list[Message_MapProperty]
    ignore_dir: bool
    desc: bytes
    attribute: Message_MapAttribute

# message Message_AdvancedLine {
#     string class_name = 1;   //the class_name from the Message_AdvancedObjectDefine
#     string instance_name = 2;// the name of this instance
#     Message_MapLine line = 3;
#     repeated Message_MapProperty property = 4; // write in json
#     bytes desc = 8;
#     Message_MapAttribute attribute = 10;
# }
class Message_AdvancedLine:
    class_name: str
    instance_name: str
    line: Message_MapLine
    property: list[Message_MapProperty]
    desc: bytes
    attribute: Message_MapAttribute

# message Message_AdvancedCurve {
#     string class_name = 1;   //the class_name from the Message_AdvancedObjectDefine
#     string instance_name = 2;// the name of this instance
#     Message_AdvancedPoint start_pos = 3;
#     Message_AdvancedPoint end_pos = 4;
#     Message_MapPos control_pos1 = 5;
#     Message_MapPos control_pos2 = 6;
#     repeated Message_MapProperty property = 7; // write in json
#     bytes desc = 8;
#     Message_MapPos control_pos3 = 9;
#     Message_MapPos control_pos4 = 10;
#     repeated Message_Device devices = 12;
#     Message_MapAttribute attribute = 15;
# }
class Message_AdvancedCurve:
    class_name: str
    instance_name: str
    start_pos: Message_AdvancedPoint
    end_pos: Message_AdvancedPoint
    control_pos1: Message_MapPos
    control_pos2: Message_MapPos
    property: list[Message_MapProperty]
    desc: bytes
    control_pos3: Message_MapPos
    control_pos4: Message_MapPos
    devices: list[Message_Device]
    attribute: Message_MapAttribute

# message Message_AdvancedArea {
#     string class_name = 1;//the class_name from the Message_AdvancedObjectDefine
#     string instance_name = 2;// the name of this instance
#     repeated Message_MapPos pos_group = 3; // usually four lines in a group
#     double dir = 4;
#     repeated Message_MapProperty property = 5; // write in json
#     bytes desc = 8;
#     repeated Message_Device devices = 10;
#     Message_MapAttribute attribute = 15;
# }
class Message_AdvancedArea:
    class_name: str
    instance_name: str
    pos_group: list[Message_MapPos]
    dir: float
    property: list[Message_MapProperty]
    desc: bytes
    devices: list[Message_Device]
    attribute: Message_MapAttribute

# message Message_VirtualLineList {
#     repeated Message_MapLine virtual_map_line = 1;
# }
class Message_VirtualLineList:
    virtual_map_line: list[Message_MapLine]

# message Message_LaserDevice {
#     uint32 id = 1;
#     repeated Message_MapPos laser_margin_pos = 2;
# }

class Message_LaserDevice:
    id: int
    laser_margin_pos: list[Message_MapPos]

# message Message_Device {
#     string model_name = 1;
#     repeated Message_LaserDevice laser_devices = 5;
#     repeated double ultrasonic_dist = 6; // dist = -1 means not used
#     repeated double fallingdown_dist = 7; // dist = -1 means not used
# }
class Message_Device:
    model_name: str
    laser_devices: list[Message_LaserDevice]
    ultrasonic_dist: list[float]
    fallingdown_dist: list[float]

# message Message_PatrolRouteStation {
#     string id = 1;
# }
class Message_PatrolRouteStation:
    id: str

# message Message_PatrolRoute {
#     string name = 1;
#     repeated Message_PatrolRouteStation station_list = 2;
#     google.protobuf.DoubleValue max_speed = 4;
#     google.protobuf.DoubleValue max_acc = 5;
#     google.protobuf.DoubleValue max_rot = 6;
#     google.protobuf.DoubleValue max_rot_acc = 7;
#     bytes desc = 8;
#     google.protobuf.DoubleValue max_dec = 9;
#     google.protobuf.DoubleValue max_rot_dec = 10;
# }
class Message_PatrolRoute:
    name: str
    station_list: list[Message_PatrolRouteStation]
    max_speed: float
    max_acc: float
    max_rot: float
    max_rot_acc: float
    desc: bytes
    max_dec: float
    max_rot_dec: float

# message Message_Primitive {
#     string class_name = 1;   //the class_name from the Message_AdvancedObjectDefine
#     string instance_name = 2;// the name of this instance
#     Message_AdvancedPoint start_pos = 3;
#     Message_AdvancedPoint end_pos = 4;
#     repeated Message_MapPos control_pos_list = 5;
#     repeated Message_MapProperty property = 6; // write in json
#     bytes desc = 7;
#     Message_MapAttribute attribute = 8;
# }
class Message_Primitive:
    class_name: str
    instance_name: str
    start_pos: Message_AdvancedPoint
    end_pos: Message_AdvancedPoint
    control_pos_list: list[Message_MapPos]
    property: list[Message_MapProperty]
    desc: bytes
    attribute: Message_MapAttribute

# message Message_ExternalDevice {
#     string class_name = 1;   //the class_name from the Message_AdvancedObjectDefine
#     string instance_name = 2;// the name of this instance
#     bool is_enabled = 3;
#     repeated Message_MapProperty property = 4; // write in json
#     bytes desc = 5;
#     Message_MapAttribute attribute = 6;
# }
class Message_ExternalDevice:
    class_name: str
    instance_name: str
    is_enabled: bool
    property: list[Message_MapProperty]
    desc: bytes
    attribute: Message_MapAttribute

# message Message_BinLocation { //库位
# 	string class_name = 1;                        //库位class_name
#     string instance_name = 2;                     //库位唯一值
# 	string group_name = 3;                        //库区名称 //弃用，已移到 message_rds_scene.proto中
# 	string point_name = 4;                        //关联的站点名称
#     Message_MapPos pos = 5;
#     repeated Message_MapProperty property = 6;    //拓展属性
#     bytes desc = 7;
#     Message_MapAttribute attribute = 8;
# }
class Message_BinLocation:
    class_name: str
    instance_name: str
    group_name: str
    point_name: str
    pos: Message_MapPos
    property: list[Message_MapProperty]
    desc: bytes
    attribute: Message_MapAttribute

# message Message_BinLocations {//库位数组   (x,y相同的库位放到一个数组中)
# 	repeated Message_BinLocation bin_location_list = 1;//库位
# }
class Message_BinLocations:
    bin_location_list: list[Message_BinLocation]

# message Message_Map {
#     string map_directory = 1;
#     Message_MapHeader header = 2;
#     repeated Message_MapPos normal_pos_list = 3;              //普通点
#     repeated Message_MapLine normal_line_list = 4;            //普通线
#     repeated Message_MapPos normal_pos3d_list = 5;            //普通3d点云
#     repeated Message_AdvancedPoint advanced_point_list = 6;   //站点
#     repeated Message_AdvancedLine  advanced_line_list = 7;    //禁行线
#     repeated Message_AdvancedCurve advanced_curve_list = 8;   //连接线
#     repeated Message_AdvancedArea  advanced_area_list = 9;    //高级区域
#     repeated Message_PatrolRoute patrol_route_list = 10;      //
#     repeated Message_MapRSSIPos rssi_pos_list = 11;           //反光板点
#     repeated Message_ReflectorPos reflector_pos_list = 12;    //反光板/反光柱
#     repeated Message_tagPos tag_pos_list = 13;                //二维码
#     repeated Message_Primitive primitive_list = 14;           //图元
#     repeated Message_ExternalDevice external_device_list = 15; //外部设备
#     repeated Message_BinLocations bin_locations_list = 16;     //库位
#
#     repeated Message_MapProperty user_data = 100;              //支持地图中自定义一些属性
# }
class Message_Map:
    map_directory: str
    header: Message_MapHeader
    normal_pos_list: list[Message_MapPos]
    normal_line_list: list[Message_MapLine]
    normal_pos3d_list: list[Message_MapPos]
    advanced_point_list: list[Message_AdvancedPoint]
    advanced_line_list: list[Message_AdvancedLine]
    advanced_curve_list: list[Message_AdvancedCurve]
    advanced_area_list: list[Message_AdvancedArea]
    patrol_route_list: list[Message_PatrolRoute]
    rssi_pos_list: list[Message_MapRSSIPos]
    reflector_pos_list: list[Message_ReflectorPos]
    tag_pos_list: list[Message_tagPos]
    primitive_list: list[Message_Primitive]
    external_device_list: list[Message_ExternalDevice]
    bin_locations_list: list[Message_BinLocations]
    user_data: list[Message_MapProperty]

# message Message_Map3D {
#     string map_directory = 1;
#     Message_MapHeader header = 2;
#     repeated Message_MapPos normal_pos3d_list = 3;            //普通3d点云
# }
class Message_Map3D:
    map_directory: str
    header: Message_MapHeader
    normal_pos3d_list: list[Message_MapPos]

