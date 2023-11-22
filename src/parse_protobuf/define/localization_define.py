from src.parse_protobuf.define.header_define import Message_Header


# message Message_Localization {
# 	enum UpdateReason {
# 		None = 0;
# 		OdoUpdate = 1;
# 		LaserCorrec = 2;
# 		LaserThenOdo = 3;
#                 PGVCORRECT = 4;
# 	}
# 	Message_Header header = 1;
# 	double x = 2;
# 	double y = 3;
# 	double angle = 4;
# 	double confidence = 5;
# 	repeated double correction_errs = 6;
# 	repeated double reliabilities = 7;
# 	bool in_forbidden_area = 8;
# 	UpdateReason update_reason = 9;
#         enum LocState {
#              Normal = 0;
#              Skidding = 1;
#              LowConfidence = 2;
#         }
#         LocState loc_state = 10;
#         double similarity = 11;
#        enum LocMethod
#        {
#           PF_LASER_2D = 0;
#           SLAM_2D = 1;
#           PGV = 2;
#           REFLECTOR = 3;
#           LASER_3D = 4;
#           BAR_CODE = 5;
#        }
#       LocMethod loc_method = 12;
# }


class Message_Localization:
    class UpdateReason:
        _None = 0
        OdoUpdate = 1
        LaserCorrec = 2
        LaserThenOdo = 3
        PGVCORRECT = 4

    header: Message_Header
    x: float
    y: float
    angle: float
    confidence: float
    correction_errs: list[float]
    reliabilities: list[float]
    in_forbidden_area: bool
    update_reason: UpdateReason

    class LocState:
        Normal = 0
        Skidding = 1
        LowConfidence = 2

    loc_state: LocState
    similarity: float

    class LocMethod:
        PF_LASER_2D = 0
        SLAM_2D = 1
        PGV = 2
        REFLECTOR = 3
        LASER_3D = 4
        BAR_CODE = 5

    loc_method: LocMethod


# message Message_LocFinished{
# 	bool value = 1;
# }
class Message_LocFinished:
    value: bool


# message Message_3DPose{
#   Message_Header header = 1;
#
#   double x = 2;
#   double y = 3;
#   double z = 4;
#
#   double q_w = 5;
#   double q_x = 6;
#   double q_y = 7;
#   double q_z = 8;
#
#   string extra_data = 9;
# }

class Message_3DPose:
    header: Message_Header
    x: float
    y: float
    z: float
    q_w: float
    q_x: float
    q_y: float
    q_z: float
    extra_data: str


# // 红外相机定位消息发布
# message Message_IRCAMPose{
#   Message_3DPose pose = 1;
# }

class Message_IRCAMPose:
    pose: Message_3DPose
