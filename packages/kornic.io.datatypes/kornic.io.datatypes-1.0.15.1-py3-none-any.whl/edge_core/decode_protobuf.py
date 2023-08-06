import edge_core.datatypes.io_property_pb2 as io_prop
import edge_core.datatypes.sinker_payload_pb2 as sinker_payload


def get_io_value(res_dataset: sinker_payload.ResponseIoDataset):
    if res_dataset.dataset_type == io_prop.DatasetType.MULTI:
        timestamp_list = res_dataset.multi_io_value.ts_array
        if res_dataset.data_type == io_prop.DataType.SINT32:
            data_value_list = res_dataset.multi_io_value.sint32_array
        elif res_dataset.data_type == io_prop.DataType.SINT64:
            data_value_list = res_dataset.multi_io_value.sint64_array
        elif res_dataset.data_type == io_prop.DataType.UINT32:
            data_value_list = res_dataset.multi_io_value.uint32_array
        elif res_dataset.data_type == io_prop.DataType.UINT64:
            data_value_list = res_dataset.multi_io_value.uint64_array
        elif res_dataset.data_type == io_prop.DataType.FLOAT:
            data_value_list = res_dataset.multi_io_value.float_array
        elif res_dataset.data_type == io_prop.DataType.DOUBLE:
            data_value_list = res_dataset.multi_io_value.double_array
        elif res_dataset.data_type == io_prop.DataType.STRING:
            data_value_list = res_dataset.multi_io_value.string_array
        elif res_dataset.data_type == io_prop.DataType.BYTES:
            data_value_list = res_dataset.multi_io_value.bytes_array
        elif res_dataset.data_type == io_prop.DataType.BOOL:
            data_value_list = res_dataset.multi_io_value.bool_array
        else:
            raise ValueError(f'not support data type : {res_dataset.data_type}')
    else:
        timestamp_list = [res_dataset.single_io_value.timestamp]
        if res_dataset.data_type == io_prop.DataType.SINT32:
            data_value_list = [res_dataset.single_io_value.io_value.sint32_value]
        elif res_dataset.data_type == io_prop.DataType.SINT64:
            data_value_list = [res_dataset.single_io_value.io_value.sint64_value]
        elif res_dataset.data_type == io_prop.DataType.UINT32:
            data_value_list = [res_dataset.single_io_value.io_value.uint32_value]
        elif res_dataset.data_type == io_prop.DataType.UINT64:
            data_value_list = [res_dataset.single_io_value.io_value.uint64_value]
        elif res_dataset.data_type == io_prop.DataType.FLOAT:
            data_value_list = [res_dataset.single_io_value.io_value.float_value]
        elif res_dataset.data_type == io_prop.DataType.DOUBLE:
            data_value_list = [res_dataset.single_io_value.io_value.double_value]
        elif res_dataset.data_type == io_prop.DataType.STRING:
            data_value_list = [res_dataset.single_io_value.io_value.string_value]
        elif res_dataset.data_type == io_prop.DataType.BYTES:
            data_value_list = [res_dataset.single_io_value.io_value.bytes_value]
        elif res_dataset.data_type == io_prop.DataType.BOOL:
            data_value_list = [res_dataset.single_io_value.io_value.bool_value]
        else:
            raise ValueError(f'not support data type : {res_dataset.data_type}')

    return timestamp_list, data_value_list


def decode_res_sink_data(pb_data: sinker_payload.ResponseFromSinker):
    response = sinker_payload.ResponseFromSinker()
    response.ParseFromString(pb_data)
    return response
