# Deployment notes

Deployed using docker compose with the dockerfile.

Change settings or docker env to reflect the database
connection.

Deployed to GCP behind regional VPC tnsquery-network.
Private services access (one-time)
via Google Service Networking API, since managed DB,
using tnsquery-network-ip-range for IP alloc.

Artifact Registry to register and host the container.
Cloud Run to build and deploy API.

DB:
tnsquery-db
Serverless VPC connection
private-ip

## build & deploy

```bash
docker-compose --project-directory . build --no-cache
```

Remote connection:
cloud-sql-auth-proxy (installed and running on docker)
gcloud auth activate-service-account --key-file=/path/to/file

```bash
docker tag <image> <region>-docker.pkg.dev/<project-id>/repository/project-name:tag
docker push
```
