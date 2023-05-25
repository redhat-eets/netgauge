from marshmallow import fields, Schema


class ResultSchema(Schema):
    tx_l1_bps = fields.Float(
        required=True, error_messages={"required": "tx_l1_bps is required."}
    )
    tx_l2_bps = fields.Float(
        required=True, error_messages={"required": "tx_l2_bps is required."}
    )
    tx_pps = fields.Float(
        required=True, error_messages={"required": "tx_pps is required."}
    )
    rx_l1_bps = fields.Float(
        required=True, error_messages={"required": "rx_l1_bps is required."}
    )
    rx_l2_bps = fields.Float(
        required=True, error_messages={"required": "rx_l2_bps is required."}
    )
    rx_pps = fields.Float(
        required=True, error_messages={"required": "rx_pps is required."}
    )
    rx_latency_minimum = fields.Float(
        required=True, error_messages={"required": "rx_latency_minimum is required."}
    )
    rx_latency_maximum = fields.Float(
        required=True, error_messages={"required": "rx_latency_maximum is required."}
    )
    rx_latency_average = fields.Float(
        required=True, error_messages={"required": "rx_latency_average is required."}
    )


class StartSchema(Schema):
    l3 = fields.Bool(required=True, error_messages={"required": "l3 is required."})
    device_pairs = fields.String(
        required=True, error_messages={"required": "device_pairs is required."}
    )
    search_runtime = fields.Int(
        required=True, error_messages={"required": "search_runtime is required."}
    )
    validation_runtime = fields.Int(
        required=True, error_messages={"required": "validation_runtime is required."}
    )
    num_flows = fields.Int(
        required=True, error_messages={"required": "num_flows is required."}
    )
    frame_size = fields.Int(
        required=True, error_messages={"required": "frame_size is required."}
    )
    max_loss_pct = fields.Float(
        required=True, error_messages={"required": "max_loss_pct is required."}
    )
    sniff_runtime = fields.Int(
        required=True, error_messages={"required": "sniff_runtime is required."}
    )
    search_granularity = fields.Float(
        required=True, error_messages={"required": "search_granularity is required."}
    )
    binary_search_extra_args = fields.List(fields.String(), required=False)


class StartSchemal3(StartSchema):
    dst_macs = fields.String(
        required=True, error_messages={"required": "dst_macs is required."}
    )


class PortSchema(Schema):
    hw_mac = fields.String(
        required=True, error_messages={"required": "hw_mac is required."}
    )
