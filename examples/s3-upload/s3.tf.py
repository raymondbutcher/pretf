import os
import re
from pathlib import Path

from pretf.api import tf
from pretf.collections import collect


@collect
def aws_s3_bucket_objects(var):
    """
    Creates aws_s3_bucket_object resources
    for all files in the given source directory.

    """

    # Inputs.
    yield tf("variable.bucket")
    yield tf("variable.prefix", {"default": ""})
    yield tf("variable.source")

    # Get the resource name of the bucket,
    # to be used in object resource names.
    bucket_resource_name = get_resource_name(var.bucket)

    total_files = 0
    total_bytes = 0

    # Resources.
    for path in Path(var.source).rglob("*"):
        if path.is_file():
            key = f"{var.prefix}{path.relative_to(var.source)}"
            resource_name = clean_resource_name(f"{bucket_resource_name}/{key}")
            yield tf(
                f"resource.aws_s3_bucket_object.{resource_name}",
                {"bucket": var.bucket.id, "key": key, "source": path},
            )
            total_files += 1
            total_bytes += os.path.getsize(path)

    # Outputs.
    yield tf("output.total_files", {"value": total_files})
    yield tf("output.total_bytes", {"value": total_bytes})


def clean_resource_name(name):
    """
    Returns the string sanitized for use as a resource name.

    """

    return re.sub(r"__+", "_", re.sub(r"[^a-zA-Z0-9]", "_", name))


def get_resource_name(block):
    """
    Returns the resource name of a tf() object.

    """

    return str(block).split(".")[-1]


def terraform(var):
    """
    This demonstrates recursively uploading files to an S3 bucket.

    """

    # Create an S3 bucket.
    bucket = yield tf(
        "resource.aws_s3_bucket.pretf_test_s3_upload",
        {
            "bucket": "pretf-test-s3-upload",
            "acl": "private",
            "server_side_encryption_configuration": {
                "rule": {
                    "apply_server_side_encryption_by_default": {
                        "sse_algorithm": "AES256"
                    }
                }
            },
        },
    )

    # Upload all files from the "files" directory.
    objects = yield aws_s3_bucket_objects(bucket=bucket, source="files")

    # Output some stats.
    yield tf("output.total_files", {"value": objects.total_files})
    yield tf("output.total_bytes", {"value": objects.total_bytes})
