import enum

from parse_protobuf.define.map_define import Message_MapPos, Message_MapProperty, Message_MapAttribute, \
    Message_ExternalDevice, Message_BinLocations, Message_AdvancedArea, Message_AdvancedCurve, Message_AdvancedPoint


# message Message_Robot { //机器人
#     string id = 1;
# 	repeated Message_MapProperty property = 2;  //机器人属性(颜色:color等)
# }

class Message_Robot:
    id: str
    property: list[Message_MapProperty]


# message Message_RobotGroup {//机器人组
# 	string name = 1;                            //组名(唯一值)
# 	repeated Message_Robot robot = 2;           // 机器人
# 	repeated Message_MapProperty property = 3;  //机器人组属性(颜色:color等)
# 	bytes desc = 4;
#     Message_MapAttribute attribute = 5;
# }

class Message_RobotGroup:
    name: str
    robot: list[Message_Robot]
    property: list[Message_MapProperty]
    desc: bytes
    attribute: Message_MapAttribute


# message Message_Wall {//墙
# 	string name = 1;                            //唯一值
# 	repeated Message_MapPos pos_list = 2;       //多边形
# 	repeated Message_MapProperty property = 3;  //墙
# 	bytes desc = 4;
#     Message_MapAttribute attribute = 5;
# }

class Message_Wall:
    name: str
    pos_list: list[Message_MapPos]
    property: list[Message_MapProperty]
    desc: bytes
    attribute: Message_MapAttribute


# message Message_3DFurniture {//模型
# 	string name = 1;                            //唯一值
# 	Message_MapPos pos = 2;                     //坐标
# 	repeated Message_MapProperty property = 3;  //模型属性
# 	bytes desc = 4;
#     Message_MapAttribute attribute = 5;
# }

class Message_3DFurniture:
    name: str
    pos: Message_MapPos
    property: list[Message_MapProperty]
    desc: bytes
    attribute: Message_MapAttribute


# message Message_RobotLabel {//机器人标签
# 	string name = 1;                            //标签名
# 	repeated string robot_ids = 2;              //机器人的ID
# 	repeated Message_MapProperty property = 3;  //标签属性
# 	bytes desc = 4;
# }

class Message_RobotLabel:
    name: str
    robot_ids: list[str]
    property: list[Message_MapProperty]
    desc: bytes


# message Message_Maps {//地图组
# 	string robot_id = 1;                        //机器人ID
# 	string map_name = 2;                        //机器人地图名
# 	string md5 = 3;                             //机器人地图的md5值
# }

class Message_Maps:
    robot_id: str
    map_name: str
    md5: str


# message Message_BlockGroup {//互斥组
# 	string name = 1;                            //互斥组名
# 	repeated string block_name = 2;             //图元instance_name(唯一)
# 	repeated Message_MapProperty property = 3;  //互斥组属性(颜色:color等)
# }

class Message_BlockGroup:
    name: str
    block_name: list[str]
    property: list[Message_MapProperty]


# message Message_LogicalMap {//逻辑地图
#     repeated Message_AdvancedPoint advanced_points = 1;   //高级点集合
# 	repeated Message_AdvancedCurve advanced_curves = 2;   //高级线集合
#     repeated Message_AdvancedArea advanced_blocks = 3;    //互斥区域集合
# 	repeated Message_BinLocations bin_locations_list = 4;   //库位集合
# 	repeated Message_Wall walls_list = 5;                   //墙
# 	repeated Message_3DFurniture models_list = 6;                   //模型
# 	repeated Message_3DFurniture windows_list = 7;                   //窗
# 	repeated Message_ExternalDevice external_device_list = 8; //外部设备
#   repeated Message_Wall work_area_list = 9;    //工作区域集合
# }

class Message_LogicalMap:
    advanced_points: list[Message_AdvancedPoint]
    advanced_curves: list[Message_AdvancedCurve]
    advanced_blocks: list[Message_AdvancedArea]
    bin_locations_list: list[Message_BinLocations]
    walls_list: list[Message_Wall]
    models_list: list[Message_3DFurniture]
    windows_list: list[Message_3DFurniture]
    external_device_list: list[Message_ExternalDevice]
    work_area_list: list[Message_Wall]


# message Message_BackgroundImage{//背景图片
# 	string file_name = 1;                       //背景图片名称,相对路径 = 场景目录/areas/区域名(注，如果是.smap则表示加载的是地图点)
# 	repeated Message_MapPos pos_list = 2;       //图片在场景中的绝对坐标(左上，右上，右下，左下)
#     repeated Message_MapProperty property = 3;  //附加属性
# }

class Message_BackgroundImage:
    file_name: str
    pos_list: list[Message_MapPos]
    property: list[Message_MapProperty]


# message Message_Area {//区域(一个场景中有多个区域)
# 	string name = 1;                              //区域名(唯一值)
# 	Message_MapPos pos = 2;                       //区域视图坐标
# 	repeated Message_Maps maps = 3;               //区域用到的机器人地图
# 	Message_LogicalMap logical_map = 4;           //逻辑地图
# 	Message_BackgroundImage background_image = 5; //背景图片
# }

class Message_Area:
    name: str
    pos: Message_MapPos
    maps: list[Message_Maps]
    logical_map: Message_LogicalMap
    background_image: Message_BackgroundImage


# message Message_Lift { //电梯
# 	string name = 1;                        //唯一值
# 	repeated string sm_name_list = 2;             //关联的SM站点名称
#     Message_MapPos pos = 3;
#     repeated Message_MapProperty property = 4;    //拓展属性
#     bytes desc = 5;
#     Message_MapAttribute attribute = 6;
# }

class Message_Lift:
    name: str
    sm_name_list: list[str]
    pos: Message_MapPos
    property: list[Message_MapProperty]
    desc: bytes
    attribute: Message_MapAttribute


# message Message_Door { //自动门
# 	string name = 1;                        //唯一值
# 	repeated string path_name_list = 2;             //关联的路径名称
#     Message_MapPos pos = 3;
#     repeated Message_MapProperty property = 4;    //拓展属性
#     bytes desc = 5;
#     Message_MapAttribute attribute = 6;
# }

class Message_Door:
    name: str
    path_name_list: list[str]
    pos: Message_MapPos
    property: list[Message_MapProperty]
    desc: bytes
    attribute: Message_MapAttribute


# message Message_BinMonitor { //库位监测
#   	string name = 1;                        //唯一值
# 	repeated string location_name_list = 2; //关联的库位名称
#     Message_MapPos pos = 3;
#     repeated Message_MapProperty property = 4;//拓展属性
#     bytes desc = 5;
#     Message_MapAttribute attribute = 6;
# }

class Message_BinMonitor:
    name: str
    location_name_list: list[str]
    pos: Message_MapPos
    property: list[Message_MapProperty]
    desc: bytes
    attribute: Message_MapAttribute


# message Message_Terminal { //终端
# 	string class_name = 1;                    //终端类别(滚筒:Roller  线边滚筒:LineEdgeRoller)
#   	string name = 2;                          //唯一值
# 	repeated string item_name_list = 3;       //关联图元名称
#     Message_MapPos pos = 4;                   //位置
#     repeated Message_MapProperty property = 5;//拓展属性
#     bytes desc = 6;                           //base64 描述
# }

class Message_Terminal:
    class_name: str
    name: str
    item_name_list: list[str]
    pos: Message_MapPos
    property: list[Message_MapProperty]
    desc: bytes


# message Message_BinArea {        //库区
# 	string name = 1;                        //唯一值
# 	repeated string location_name_list = 2; //关联的库位名称
#     Message_MapPos pos = 3;
#     repeated Message_MapProperty property = 4;//拓展属性
#     bytes desc = 5;
#     Message_MapAttribute attribute = 6;
# }

class Message_BinArea:
    name: str
    location_name_list: list[str]
    pos: Message_MapPos
    property: list[Message_MapProperty]
    desc: bytes
    attribute: Message_MapAttribute


# message Message_Scene {
# 	//string save_time = 1;                      //保存时间(已弃用)
# 	string desc = 2;                             //描述
# 	repeated Message_RobotGroup robot_group = 3; //机器人组(内部机器人不可重复)
# 	repeated Message_RobotLabel labels = 4;      //机器人标签(机器人可有多个标签)
# 	repeated Message_Area areas = 5;             //区域
# 	repeated Message_BlockGroup block_group = 6; //互斥组
# 	repeated Message_Lift lifts = 7;             //电梯
# 	repeated Message_Door doors = 8;             //自动门
# 	repeated Message_BinMonitor bin_monitors = 9;       //库位监测(视觉，其他传感器，其他服务器输入)
# 	repeated Message_BinArea bin_areas = 10;     //库区
# 	repeated Message_Terminal terminals = 11;    //终端
# }

class Message_Scene:
    desc: str
    robot_group: list[Message_RobotGroup]
    labels: list[Message_RobotLabel]
    areas: list[Message_Area]
    block_group: list[Message_BlockGroup]
    lifts: list[Message_Lift]
    doors: list[Message_Door]
    bin_monitors: list[Message_BinMonitor]
    bin_areas: list[Message_BinArea]
    terminals: list[Message_Terminal]


# message  Message_Map_Changed{
# 	string map_name = 1;
# 	bool normal_pos_changed = 2;
# }

class Message_Map_Changed:
    map_name: str
    normal_pos_changed: bool


# message Message_Robot_Changed {
# # 	enum ChangedType {
# # 		Modified = 0;
# # 		Added = 1;
# # 		Deleted = 2;
# # 	}
# #
# # 	string robot_id = 1;							// 机器人的 id
# # 	ChangedType type = 2;							// 类型
# #
# # 	repeated Message_Map_Changed map_changed_list = 11;
# # 	bool robot_property_changed = 13;						// Message_Robot 中机器人个性化数据变了
# # }

class Message_Robot_Changed:
    class ChangedType(enum.Enum):
        Modified = 0
        Added = 1
        Deleted = 2

    robot_id: str
    type: int
    map_changed_list: list[Message_Map_Changed]
    robot_property_changed: bool


# message Message_Scene_Changes {
# 	bool logicalmap_changed = 1;
# 	bool logicalmap_property_changed = 2;						// Message_LogicalMap 中，所有元素的 property 中， 任何一个有改变
# 	repeated Message_Robot_Changed robot_changed_list = 11;
# }

class Message_Scene_Changes:
    logicalmap_changed: bool
    logicalmap_property_changed: bool
    robot_changed_list: list[Message_Robot_Changed]
