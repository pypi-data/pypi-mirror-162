from datetime import timedelta
from inspect import signature
from typing import Dict
from typing import List

import pendulum

from tecton.compat.inputs import Input
from tecton.declarative.base import FWV5BaseDataSource
from tecton.declarative.base import RequestSourceBase
from tecton.feature_services.feature_service_args import FeaturesConfig
from tecton.types import to_spark_schema_wrapper
from tecton_proto.args import feature_service_pb2
from tecton_proto.args.pipeline_pb2 import DataSourceNode
from tecton_proto.args.pipeline_pb2 import FeatureViewNode
from tecton_proto.args.pipeline_pb2 import PipelineNode
from tecton_proto.args.pipeline_pb2 import RequestContext as RequestContextProto
from tecton_proto.args.pipeline_pb2 import RequestDataSourceNode
from tecton_spark.spark_schema_wrapper import SparkSchemaWrapper
from tecton_spark.time_utils import strict_pytimeparse
from tecton_spark.time_utils import WINDOW_UNBOUNDED_PRECEDING


def inputs_to_pipeline_nodes(inputs: Dict[str, Input], fv_name) -> Dict[str, PipelineNode]:
    kwargs = {}
    for ds_name, input in inputs.items():
        pipeline_node = PipelineNode()
        if isinstance(input.source, RequestSourceBase):
            node = RequestDataSourceNode()
            schema = input.source.schema
            if isinstance(schema, List):
                wrapper = to_spark_schema_wrapper(schema)
            else:
                wrapper = SparkSchemaWrapper(schema)
            rc = RequestContextProto(schema=wrapper.to_proto())
            node.request_context.CopyFrom(rc)
            node.input_name = ds_name
            pipeline_node.request_data_source_node.CopyFrom(node)

        elif isinstance(input.source, FeaturesConfig):
            node = FeatureViewNode()
            fsc = input.source
            node.feature_view_id.CopyFrom(fsc.id)
            fsfv = feature_service_pb2.FeatureServiceFeaturePackage()
            if fsc.override_join_keys:
                fsfv.override_join_keys.extend(
                    feature_service_pb2.ColumnPair(spine_column=k, feature_column=v)
                    for k, v in sorted(fsc.override_join_keys.items())
                )
            fsfv.feature_package_id.CopyFrom(fsc.id)
            fsfv.namespace = fsc.namespace
            fsfv.features.extend(fsc.features)
            node.feature_view.CopyFrom(fsfv)
            node.input_name = ds_name
            pipeline_node.feature_view_node.CopyFrom(node)
        else:
            if isinstance(input.source, FWV5BaseDataSource):
                assert (
                    input.source.data_delay is None
                    or input.source.data_delay == timedelta(0)
                    or (
                        input.schedule_offset
                        and input.source.data_delay
                        == pendulum.duration(seconds=strict_pytimeparse(input.schedule_offset))
                    )
                ), (
                    f"When using a non-compat Data Source with a compat Feature View, the Data Source’s `data_delay` parameter"
                    f" cannot conflict with the `schedule_offset` configured in the Feature View. To resolve this, you can a)"
                    f" not set data_delay in the Data Source {ds_name}, b) set schedule_offset in Feature View {fv_name} and"
                    f" data_delay in Data Source {ds_name} to the same value, or c) upgrade the Feature View {fv_name} to a"
                    f" non-compat feature view."
                )
            # In this case we're dealing with a DataSource input type.
            node = DataSourceNode()
            node.virtual_data_source_id.CopyFrom(input.source._id)
            if input.window is not None:
                if input.window == WINDOW_UNBOUNDED_PRECEDING:
                    node.window_unbounded_preceding = True
                else:
                    node.window.FromTimedelta(pendulum.duration(seconds=strict_pytimeparse(input.window)))

            if input.schedule_offset is not None:
                node.schedule_offset.FromTimedelta(pendulum.duration(seconds=strict_pytimeparse(input.schedule_offset)))

            node.input_name = ds_name

            pipeline_node.data_source_node.CopyFrom(node)
        kwargs[ds_name] = pipeline_node

    return kwargs


def test_binding_user_function(fn, inputs):
    # this function binds the top-level pipeline function only, for transformation binding, see transformation.__call__
    pipeline_signature = signature(fn)
    try:
        pipeline_signature.bind(**inputs)
    except TypeError as e:
        raise TypeError(f"while binding inputs to pipeline function, TypeError: {e}")
