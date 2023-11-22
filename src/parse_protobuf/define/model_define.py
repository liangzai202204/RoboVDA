# message Message_Param {									// 参数 （键 - 值 - 最大值 - 最小值 - 描述 - 单位）
# 	string key = 1;
# 	string type = 2;									// "bytes","string","ip"; "bool"; "int32","uint32","int64","uint64","float","double"
# 	oneof oneof_value {
# 		string string_value = 3;
# 		bool bool_value = 4;
# 		int32 int32_value = 5;
# 		uint32 uint32_value = 6;
# 		int64 int64_value = 7;
# 		uint64 uint64_value = 8;
# 		float float_value = 9;
# 		double double_value = 10;
# 		bytes bytes_value = 11;
# 	}
# 	oneof oneof_maxValue {
# 		int32 int32_maxvalue = 12;
# 		uint32 uint32_maxvalue = 13;
# 		int64 int64_maxvalue = 14;
# 		uint64 uint64_maxvalue = 15;
# 		float float_maxvalue = 16;
# 		double double_maxvalue = 17;
#
# 	}
# 	oneof oneof_minValue {
# 		int32 int32_minvalue = 18;
# 		uint32 uint32_minvalue = 19;
# 		int64 int64_minvalue = 20;
# 		uint64 uint64_minvalue = 21;
# 		float float_minvalue = 22;
# 		double double_minvalue = 23;
# 	}
# 	string unit = 24;									// 单位：deg ,rad,m,cm,mm...
# 	string desc = 25;									// 描述(base64-方便中文显示)
#
# 	bool clone_enable = 32;								// 是否可以克隆
# }
class Message_Param:
    key: str
    type: str
    string_value: str
    bool_value: bool
    int32_value: int
    uint32_value: int
    int64_value: int
    uint64_value: int
    float_value: float
    double_value: float
    bytes_value: bytes
    int32_maxvalue: int
    uint32_maxvalue: int
    int64_maxvalue: int
    uint64_maxvalue: int
    float_maxvalue: float
    double_maxvalue: float
    int32_minvalue: int
    uint32_minvalue: int
    int64_minvalue: int
    uint64_minvalue: int
    float_minvalue: float
    double_minvalue: float
    unit: str
    desc: str
    clone_enable: bool


# message Message_ChildParam{								// 选择框单个下拉选项
# 	string key = 1;										// 键
# 	string desc = 2;									// 描述 (base64-方便中文显示)
# 	repeated Message_Param params = 11;
# }
class Message_ChildParam:
    key: str
    desc: str
    params: list[Message_Param]


# message Message_ArrayParam{								// 列表参数
# 	repeated Message_Param params = 1;					// 该列表下所有的参数列表
# }
class Message_ArrayParam:
    params: list[Message_Param]


# message Message_ComboParam{         					// 下拉选择框参数
# 	string child_key = 3;                              	// 下拉框当前的默认值（下拉列表中被选中的key）
# 	repeated Message_ChildParam child_params = 11;  	// 下拉列表
# }
class Message_ComboParam:
    child_key: str
    child_params: list[Message_ChildParam]


# message Message_DeviceParam {							// 设备参数
# 	string key = 1;										// 参数key (方便对比差异化)
# 	string desc = 2;
# 	string type = 3;									// 参数类型 (comboParam/arrayParam)
# 	oneof oneof_deviceValue {
# 		Message_ComboParam combo_param = 4;				// 下拉选择框式的数据
# 		Message_ArrayParam array_param = 5;				// 列表式的数据
# 	}
# 	bool clone_enable = 32;								// 是否可以克隆
# }
class Message_DeviceParam:
    key: str
    desc: str
    type: str
    combo_param: Message_ComboParam
    array_param: Message_ArrayParam
    clone_enable: bool


# message Message_Device {								// 设备
# 	string name = 1;                               		// 名称
# 	string desc	= 2;		                       		// 描述 (base64-方便中文显示)
# 	bool is_display = 3;                            	// 是否以图形的形式显示到界面
# 	bool is_enabled = 4;                             	// 设备是否激活使用
# 	repeated Message_DeviceParam device_params = 11; 	// 该设备下的所有参数
# }
class Message_Device:
    name: str
    desc: str
    is_display: bool
    is_enabled: bool
    device_params: list[Message_DeviceParam]


# message Message_DeviceType {							// 设备类型
# 	uint32 ord = 1;                                		// 用于界面图层显示顺序
# 	string name = 2;                               		// 名称
# 	string desc	= 3;		                       		// 描述 (base64-方便中文显示)
# 	uint32 maxCount = 4;                           		// 设备最大数量 (缺省或=0表示不限制)
# 	repeated Message_Device devices = 11;           	// 该设备类型下所有设备
# }
class Message_DeviceType:
    ord: int
    name: str
    desc: str
    maxCount: int
    devices: list[Message_Device]


# message Message_Model {
# 	string model = 1;									// 模型文件名称
# 	repeated Message_DeviceType device_types = 11;   	// 所有设备类型
# }
class Message_Model:
    model: str
    device_types: list[Message_DeviceType]
