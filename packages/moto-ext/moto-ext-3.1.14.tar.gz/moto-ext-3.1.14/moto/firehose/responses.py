"""Handles Firehose API requests, invokes method and returns response."""
import json

from moto.core.responses import BaseResponse
from .models import firehose_backends


class FirehoseResponse(BaseResponse):
    """Handler for Firehose requests and responses."""

    @property
    def firehose_backend(self):
        """Return backend instance specific to this region."""
        return firehose_backends[self.region]

    def create_delivery_stream(self):
        """Prepare arguments and respond to CreateDeliveryStream request."""
        delivery_stream_arn = self.firehose_backend.create_delivery_stream(
            self.region,
            self._get_param("DeliveryStreamName"),
            self._get_param("DeliveryStreamType"),
            self._get_param("KinesisStreamSourceConfiguration"),
            self._get_param("DeliveryStreamEncryptionConfigurationInput"),
            self._get_param("S3DestinationConfiguration"),
            self._get_param("ExtendedS3DestinationConfiguration"),
            self._get_param("RedshiftDestinationConfiguration"),
            self._get_param("ElasticsearchDestinationConfiguration"),
            self._get_param("SplunkDestinationConfiguration"),
            self._get_param("HttpEndpointDestinationConfiguration"),
            self._get_param("Tags"),
        )
        return json.dumps({"DeliveryStreamARN": delivery_stream_arn})

    def delete_delivery_stream(self):
        """Prepare arguments and respond to DeleteDeliveryStream request."""
        self.firehose_backend.delete_delivery_stream(
            self._get_param("DeliveryStreamName"), self._get_param("AllowForceDelete")
        )
        return json.dumps({})

    def describe_delivery_stream(self):
        """Prepare arguments and respond to DescribeDeliveryStream request."""
        result = self.firehose_backend.describe_delivery_stream(
            self._get_param("DeliveryStreamName"),
            self._get_param("Limit"),
            self._get_param("ExclusiveStartDestinationId"),
        )
        return json.dumps(result)

    def list_delivery_streams(self):
        """Prepare arguments and respond to ListDeliveryStreams request."""
        stream_list = self.firehose_backend.list_delivery_streams(
            self._get_param("Limit"),
            self._get_param("DeliveryStreamType"),
            self._get_param("ExclusiveStartDeliveryStreamName"),
        )
        return json.dumps(stream_list)

    def list_tags_for_delivery_stream(self):
        """Prepare arguments and respond to ListTagsForDeliveryStream()."""
        result = self.firehose_backend.list_tags_for_delivery_stream(
            self._get_param("DeliveryStreamName"),
            self._get_param("ExclusiveStartTagKey"),
            self._get_param("Limit"),
        )
        return json.dumps(result)

    def put_record(self):
        """Prepare arguments and response to PutRecord()."""
        result = self.firehose_backend.put_record(
            self._get_param("DeliveryStreamName"), self._get_param("Record")
        )
        return json.dumps(result)

    def put_record_batch(self):
        """Prepare arguments and response to PutRecordBatch()."""
        result = self.firehose_backend.put_record_batch(
            self._get_param("DeliveryStreamName"), self._get_param("Records")
        )
        return json.dumps(result)

    def tag_delivery_stream(self):
        """Prepare arguments and respond to TagDeliveryStream request."""
        self.firehose_backend.tag_delivery_stream(
            self._get_param("DeliveryStreamName"), self._get_param("Tags")
        )
        return json.dumps({})

    def untag_delivery_stream(self):
        """Prepare arguments and respond to UntagDeliveryStream()."""
        self.firehose_backend.untag_delivery_stream(
            self._get_param("DeliveryStreamName"), self._get_param("TagKeys")
        )
        return json.dumps({})

    def update_destination(self):
        """Prepare arguments and respond to UpdateDestination()."""
        self.firehose_backend.update_destination(
            self._get_param("DeliveryStreamName"),
            self._get_param("CurrentDeliveryStreamVersionId"),
            self._get_param("DestinationId"),
            self._get_param("S3DestinationUpdate"),
            self._get_param("ExtendedS3DestinationUpdate"),
            self._get_param("S3BackupMode"),
            self._get_param("RedshiftDestinationUpdate"),
            self._get_param("ElasticsearchDestinationUpdate"),
            self._get_param("SplunkDestinationUpdate"),
            self._get_param("HttpEndpointDestinationUpdate"),
        )
        return json.dumps({})
