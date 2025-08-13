# Botoprune
Botoprune is a Python library used to reduce the installed size of botocore by removing unnecessary AWS api data.

## Using Botoprune

The chief application of this library is in the building of small Docker images. Because docker images are built in layers, any file created in one layer still takes up spaces in the final image. This means that Botoprune must be run in the same RUN instruction that installs boto3/botocore preventing the unnecessary data from being committed to the final layer.

```
# Docker step to install boto3 and remove all API data except s3, ec2, and kms.
RUN pip install --no-cache-dir --no-compile \
        boto3 \
        botoprune && \
    python -m botoprune.whitelist s3 ec2 kms
```

Botoprune also supports more targeted removal of specific services. This offers more control but results in less space savings compared to whitelisting.

```
   # Remove the API data for bedrock, rds, and sts.
   python -m botoprune.remove bedrock rds sts
```
