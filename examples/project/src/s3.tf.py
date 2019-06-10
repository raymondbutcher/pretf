from pretf.api import tf


def terraform(var):

    name = f"pretf-test-{var.envname}"

    bucket = yield tf("resource.aws_s3_bucket.test", {"bucket": name, "acl": "private"})

    # Loop through all dogs specified in this environment.
    for name in var.dogs:

        # Use a module to determine the number of barks by this dog.
        barks = yield tf(f"module.{name}_barks", {"source": "./barks"})

        # Write a story to S3.
        story = yield tf(
            f"resource.aws_s3_bucket_object.{name}",
            {
                "bucket": bucket.id,
                "key": f"{name}.txt",
                "content": f"{name} barked {barks.count} times",
            },
        )

        # Also output the story.
        yield tf(f"output.{name}", {"value": story.content})
