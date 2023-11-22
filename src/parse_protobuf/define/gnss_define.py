from src.parse_protobuf.define.header_define import Message_Header


# // 安装信息
# message Message_GnssInstallInfo {
#     double x = 1;
#     double y = 2;
#     double z = 3;
#     double yaw = 4;
#     // double qx = 4;
#     // double qy = 5;
#     // double qz = 6;
#     // double qw = 7;
# }
class Message_GnssInstallInfo:
    x: float
    y: float
    z: float
    yaw: float
# // ENU坐标参考位置信息
# message Message_GnssRefInfo {
#     // 经度 [degrees]
#     double longitude = 1;
#     // 纬度 [degrees]
#     double latitude = 2;
#     // 高度 [m]
#     double altitude = 3;
# }
class Message_GnssRefInfo:
    longitude: float
    latitude: float
    altitude: float
# message Message_GNSS {
#     Message_Header header = 1;
#     // 当前定位状态
#     // 0 = No fix, 1 = autonomous GNSS fix, 2 = differential GNSS fix, 4 = RTK fixed,
#     // 5 = RTK float, 6 = estimated/dead reckoning fix
#     int32 status = 2;
#     // 天线在地图坐标系下的x位置，x [m]
#     double x = 3;
#     // 天线在地图坐标系下的y位置，y [m]
#     double y = 4;
#     // 以基站位置为参考系的ENU坐标，z [m]
#     double z = 5;
#     // UBX 2D 水平位置精度 [m]
#     double ubx_2d_acc_h = 7;
#     // UBX 2D 垂直位置精度 [m]
#     double ubx_2d_acc_v = 8;
#     // UBX 3D 位置精度 [m]
#     double ubx_3d_acc = 9;
#     // 经度 [degrees]
#     double longitude = 10;
#     // 纬度 [degrees]
#     double latitude = 11;
#     // 高度 [m]
#     double altitude = 12;
#     // 安装信息
#     Message_GnssInstallInfo install_info = 13;
#     // ENU坐标参考位置信息
#     Message_GnssRefInfo ref_info = 14;
#     // 天线在ENU坐标系下的x位置，x [m]
#     double enu_x = 15;
#     // 天线在ENU坐标系下的y位置，y [m]
#     double enu_y = 16;
#     // 朝向信息
#     double heading = 17;
# }
class Message_GNSS:
    header: Message_Header
    status: int
    x: float
    y: float
    z: float
    ubx_2d_acc_h: float
    ubx_2d_acc_v: float
    ubx_3d_acc: float
    longitude: float
    latitude: float
    altitude: float
    install_info: Message_GnssInstallInfo
    ref_info: Message_GnssRefInfo
    enu_x: float
    enu_y: float
    heading: float
# message Message_AllGNSS{
#     repeated Message_GNSS gnss = 1;
# }
class Message_AllGNSS:
    gnss: list[Message_GNSS]