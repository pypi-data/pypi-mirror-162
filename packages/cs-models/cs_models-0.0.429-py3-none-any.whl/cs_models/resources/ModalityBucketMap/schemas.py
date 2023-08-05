from marshmallow import (
    Schema,
    fields,
    validate,
)


class ModalityBucketMapResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    modality_id = fields.Integer(required=True)
    modality_bucket_id = fields.Integer(required=True)
    is_deleted = fields.Boolean(allow_none=True)
    updated_at = fields.DateTime()
