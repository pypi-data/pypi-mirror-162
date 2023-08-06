import boto3

s3 = boto3.resource('s3')


def create_bucket(bucket_name: str, region: str):

    try:
        buckets = s3.buckets.all()

        if bucket_name in [bucket.name for bucket in buckets]:
            return bucket_name

        bucket = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={
                                "LocationConstraint": region})
        return bucket
    except Exception as e:
        print(e)
        return bucket_name
