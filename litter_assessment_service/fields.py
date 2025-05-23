from webargs import validate
from marshmallow import Schema, fields

class PredictArgsSchema(Schema):
    class Meta:
        ordered = True

    files= fields.Field(
        required=True,
        type="file",
        location="form",
        description="Input the image you want to analyse")

    PLD_plot = fields.Bool(
        required = False,
        load_default=True,
        description='Whether a detection plot should be provided.',
        metadata={"enum": [True, False]})

    PLQ_plot = fields.Bool(
        required = False,
        load_default=True,
        description='Whether a quantification plot should be provided.',
        metadata={"enum": [True, False]})
    
    face_detection = fields.Bool(
        required = False,
        load_default=False,
        description='Whether the face detection model analyses the image first.',
        metadata={"enum": [True, False]})

    accept = fields.Str(
        location="headers",
        validate=validate.OneOf(['application/zip']),
        # validate=validate.OneOf(['application/zip', 'image/png']),
        # FIXME: "image/png" accept option is not working as expected, because it
        # returns a ZIP, not an image
        description='Choose zip if you want PLD and PLQ')

    output_type = fields.Str(
        load_default='Download',
        metadata={"enum": ['Download', 'Nextcloud']},
        description='Choose the way the output should be provided')

if __name__=='__main__':
    args=PredictArgsSchema()
