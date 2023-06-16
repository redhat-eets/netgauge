from marshmallow import fields, Schema


class ResultSchema(Schema):
    rx_l1_bps = fields.Float(
        required=True, error_messages={"required": "rx_l1_bps is required."}
    )
    rx_l2_bps = fields.Float(
        required=True, error_messages={"required": "rx_l2_bps is required."}
    )
    rx_packets = fields.Int(
        required=True, error_messages={"required": "rx_packets is required."}
    )
    rx_lost_packets = fields.Int(
        required=True, error_messages={"required": "rx_lost_packets is required."}
    )
    rx_lost_packets_pct = fields.Float(
        required=True, error_messages={"required": "rx_lost_packets_pct is required."}
    )
    rx_pps = fields.Float(
        required=True, error_messages={"required": "rx_pps is required."}
    )
    rx_lost_pps = fields.Float(
        required=True, error_messages={"required": "rx_lost_pps is required."}
    )
    rx_latency_average = fields.Float(
        required=True, error_messages={"required": "rx_latency_average is required."}
    )
    rx_latency_packets = fields.Int(
        required=True, error_messages={"required": "rx_latency_packets is required."}
    )
    rx_latency_maximum = fields.Float(
        required=True, error_messages={"required": "rx_latency_maximum is required."}
    )
    rx_latency_minimum = fields.Float(
        required=True, error_messages={"required": "rx_latency_minimum is required."}
    )
    rx_latency_l1_bps = fields.Float(
        required=True, error_messages={"required": "rx_latency_l1_bps is required."}
    )
    rx_latency_l2_bps = fields.Float(
        required=True, error_messages={"required": "rx_latency_l2_bps is required."}
    )
    rx_latency_pps = fields.Float(
        required=True, error_messages={"required": "rx_latency_pps is required."}
    )
    rx_latency_lost_pps = fields.Float(
        required=True, error_messages={"required": "rx_latency_lost_pps is required."}
    )
    rx_active = fields.Boolean(
        required=True, error_messages={"required": "rx_active is required."}
    )
    tx_l1_bps = fields.Float(
        required=True, error_messages={"required": "tx_l1_bps is required."}
    )
    tx_l2_bps = fields.Float(
        required=True, error_messages={"required": "tx_l2_bps is required."}
    )
    tx_packets = fields.Int(
        required=True, error_messages={"required": "tx_packets is required."}
    )
    tx_pps = fields.Float(
        required=True, error_messages={"required": "tx_pps is required."}
    )
    tx_pps_target = fields.Float(
        required=True, error_messages={"required": "tx_pps_target is required."}
    )
    tx_latency_packets = fields.Int(
        required=True, error_messages={"required": "tx_latency_packets is required."}
    )
    tx_latency_l1_bps = fields.Float(
        required=True, error_messages={"required": "tx_latency_l1_bps is required."}
    )
    tx_latency_l2_bps = fields.Float(
        required=True, error_messages={"required": "tx_latency_l2_bps is required."}
    )
    tx_latency_pps = fields.Float(
        required=True, error_messages={"required": "tx_latency_pps is required."}
    )
    tx_active = fields.Boolean(
        required=True, error_messages={"required": "tx_active is required."}
    )
    tx_tolerance_min = fields.Float(
        required=True, error_messages={"required": "tx_tolerance_min is required."}
    )
    tx_tolerance_max = fields.Float(
        required=True, error_messages={"required": "tx_tolerance_max is required."}
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
    active_device_pairs = fields.String(required=False)
    traffic_direction = fields.String(required=False)
    rate_tolerance_failure = fields.String(required=False)
    duplicate_packet_failure = fields.String(required=False)
    negative_packet_loss = fields.String(required=False)
    send_teaching_warmup = fields.Boolean(required=False)
    teaching_warmup_packet_type = fields.String(required=False)
    teaching_warmup_packet_rate = fields.Int(required=False)
    use_src_ip_flows = fields.Boolean(required=False)
    use_dst_ip_flows = fields.Boolean(required=False)
    use_src_mac_flows = fields.Boolean(required=False)
    use_dst_mac_flows = fields.Boolean(required=False)
    rate_unit = fields.String(required=False)
    rate = fields.Int(required=False)
    one_shot = fields.Int(required=False)
    rate_tolerance = fields.Int(required=False)
    runtime_tolerance = fields.Int(required=False)
    no_promisc = fields.Boolean(required=False)
    binary_search_extra_args = fields.List(fields.String(), required=False)


class StartSchemal3(StartSchema):
    dst_macs = fields.String(
        required=True, error_messages={"required": "dst_macs is required."}
    )


class PortSchema(Schema):
    hw_mac = fields.String(
        required=True, error_messages={"required": "hw_mac is required."}
    )
