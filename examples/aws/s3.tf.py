import os
from pathlib import Path

from pretf.api import labels
from pretf.blocks import output, resource, variable
from pretf.collections import collect


def pretf_blocks():
    """
    This demonstrates recursively uploading files to an S3 bucket.

    """

    # Create an S3 bucket.
    bucket = yield resource.aws_s3_bucket.test(
        bucket="pretf-example-aws-files",
        acl="private",
    )

    # Upload all files from the "files" and "more-files" directories.
    total_files = 0
    total_bytes = 0
    for source in ("files", "more-files"):
        objects = yield aws_s3_bucket_objects(
            bucket=bucket,
            source=source,
        )
        total_files += objects.total_files
        total_bytes += objects.total_bytes

    # Output some stats.
    yield output.total_files(value=total_files)
    yield output.total_bytes(value=total_bytes)


@collect
def aws_s3_bucket_objects(var):
    """
    Creates aws_s3_bucket_object resources for all files in the given
    source directory. This is using the "collections" API to create
    a reusable function that generates resources.

    """

    # Inputs.
    yield variable.bucket()
    yield variable.prefix(default="")
    yield variable.source()

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
            yield resource.aws_s3_bucket_object[object_label](
                bucket=var.bucket.id,
                key=key,
                source=path,
            )
            total_files += 1
            total_bytes += os.path.getsize(path)

    # Outputs.
    yield output.total_files(value=total_files)
    yield output.total_bytes(value=total_bytes)
