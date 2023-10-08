import uuid
import io
from minio import Minio
from app import config


def store_image(image):

    # Get S3 bucket settings from config
    settings = config.Settings()
    S3_ENDPOINT_URL = settings.S3_ENDPOINT_URL
    S3_BUCKET_NAME = settings.S3_BUCKET_NAME
    S3_ACCESS_KEY_ID = settings.S3_ACCESS_KEY_ID
    S3_SECRET_ACCESS_KEY = settings.S3_SECRET_ACCESS_KEY

    # Initialize Minio client
    try:
        client = Minio(
            S3_ENDPOINT_URL,
            access_key=S3_ACCESS_KEY_ID,
            secret_key=S3_SECRET_ACCESS_KEY,
            secure=True
        )
    except Exception as e:
        raise e

    # Convert image data to bytes
    image_bytes = io.BytesIO(image)

    # Create object name
    object_name = f"{uuid.uuid4()}.jpg"

    try:
        result = client.put_object(
            S3_BUCKET_NAME,
            object_name,
            image_bytes,
            length=len(image),
            content_type='image/jpeg'
        )
        return f"{S3_ENDPOINT_URL}/{S3_BUCKET_NAME}/{object_name}"
    except Exception as e:
        raise e
