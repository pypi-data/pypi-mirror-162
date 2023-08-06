./helpers/setup_params.sh
kubectl delete service ${SERVICE_NAME}
gcloud container clusters delete ${CLUSTER_NAME}
gcloud container images delete ${IMAGE_NAME}  --force-delete-tags --quiet