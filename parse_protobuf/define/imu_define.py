from parse_protobuf.define.header_define import Message_Header


# message Message_ImuInstallInfo{
# 	double x = 1;
# 	double y = 2;
# 	double z = 3;
#     double qx = 4;
#  	double qy = 5;
#  	double qz = 6;
# 	double qw = 7;
#         double SSF = 8;
# }
class Message_ImuInstallInfo:
    x: float
    y: float
    z: float
    qx: float
    qy: float
    qz: float
    qw: float
    SSF: float
# message Message_IMU {
# 	Message_Header header = 1;
# 	double yaw = 2;
# 	double roll = 3;
# 	double pitch = 4;
# 	double acc_x = 5;
# 	double acc_y = 6;
# 	double acc_z = 7;
# 	double rot_x = 8;
# 	double rot_y = 9;
# 	double rot_z = 10;
# 	int32 rot_off_x = 11;
# 	int32 rot_off_y = 12;
# 	int32 rot_off_z = 13;
# 	double qx = 14;
# 	double qy = 15;
# 	double qz = 16;
# 	double qw = 17;
# 	Message_ImuInstallInfo install_info = 18;
# }
class Message_IMU:
    header: Message_Header
    yaw: float
    roll: float
    pitch: float
    acc_x: float
    acc_y: float
    acc_z: float
    rot_x: float
    rot_y: float
    rot_z: float
    rot_off_x: int
    rot_off_y: int
    rot_off_z: int
    qx: float
    qy: float
    qz: float
    qw: float
    install_info: Message_ImuInstallInfo