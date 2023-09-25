# message Message_Header {
# 	uint64 pub_nsec = 1;
# 	uint64 data_nsec = 2;
# 	uint64 seq = 3;
# 	string frame_id = 4;
# }
class Message_Header:
    pub_nsec: int
    data_nsec: int
    seq: int
    frame_id: str
