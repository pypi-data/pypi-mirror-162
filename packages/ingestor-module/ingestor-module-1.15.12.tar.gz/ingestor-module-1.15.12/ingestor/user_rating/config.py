"""
Compute Rating
"""
import os

import boto3

weight_duration = 100
weight_top_rating = 100
weight_very_positive = 50
weight_positive = 15
weight_not_sure = 15

DAYS = 1  # For timedelta

NUMBER_OF_BINS = 4  # For binning

SCALING_FACTOR = 10  # For normalised implicit rating

RESOLUTION = 0.5  # For rounding off partially

MILLISECONDS_IN_ONE_MINUTE = 60000  # For conversion of duration (in milliseconds) to minutes

NUMBER_OF_DUPLICATE_VIEWS_THRESHOLD = 12 # For capping the data

VISIONPLUS_DEV = "visionplus-dev"

VIEWED_DATA_PATH = "pickles/27062022/join_viewed.pkl"


aws_access_key_id: str = os.getenv(
        "AWS_ACCESS_KEY_ID", "AKIA2YVKI2GF5O6VSN7S")
aws_secret_access_key: str = os.getenv(
        "AWS_SECRET_ACCESS_KEY", "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")
region_name: str = os.getenv("AWS_REGION_NAME", "ap-southeast-1")

S3_RESOURCE = boto3.resource(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name,
)
