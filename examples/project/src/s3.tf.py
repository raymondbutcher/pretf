from pretf.api import block


def pretf_blocks(var):

    name = f"pretf-test-{var.envname}"

    bucket = yield block(
        "resource", "aws_s3_bucket", "test", {"bucket": name, "acl": "private"}
    )

    # Loop through all dogs specified in this environment.
    for name in var.dogs:

        # Use a module to determine the number of barks by this dog.
        barks = yield block("module", f"{name}_barks", {"source": "./barks"})

        # Write a story to S3.
        story = yield block(
            "resource",
            "aws_s3_bucket_object",
            name,
            {
                "bucket": bucket.id,
                "key": f"{name}.txt",
                "content": f"{name} barked {barks.count} times",
            },
        )

        # Also output the story.
        yield block("output", name, {"value": story.content})
