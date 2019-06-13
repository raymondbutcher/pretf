import os
from pathlib import Path

from pretf.api import block, labels
from pretf.collections import collect


def pretf_blocks():
    """
    This demonstrates recursively uploading files to an S3 bucket.

    """

    # Create an S3 bucket.
    bucket = yield block(
        "resource",
        "aws_s3_bucket",
        "test",
        {"bucket": "pretf-test-s3-upload", "acl": "private"},
    )

    # Upload all files from the "files" directory.
    objects = yield aws_s3_bucket_objects(bucket=bucket, source="files")

    # Output some stats.
    yield block("output", "total_files", {"value": objects.total_files})
    yield block("output", "total_bytes", {"value": objects.total_bytes})


@collect
def aws_s3_bucket_objects(var):
    """
    Creates aws_s3_bucket_object resources
    for all files in the given source directory.

    """

    # Inputs.
    yield block("variable", "bucket", {})
    yield block("variable", "prefix", {"default": ""})
    yield block("variable", "source", {})

    # Get the resource name of the bucket,
    # to be used in object resource names.
    bucket_label = labels.get(var.bucket)

    total_files = 0
    total_bytes = 0

    # Resources.
    for path in Path(var.source).rglob("*"):
        if path.is_file():
            key = f"{var.prefix}{path.relative_to(var.source)}"
            object_label = labels.clean(f"{bucket_label}/{key}")
            yield block(
                "resource",
                "aws_s3_bucket_object",
                object_label,
                {"bucket": var.bucket.id, "key": key, "source": path},
            )
            total_files += 1
            total_bytes += os.path.getsize(path)

    # Outputs.
    yield block("output", "total_files", {"value": total_files})
    yield block("output", "total_bytes", {"value": total_bytes})
