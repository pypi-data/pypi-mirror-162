#!/bin/bash

./devland/build_and_register_image_in_devland.sh

#to be run only once
./devland/gke/create_gke_cluster.sh

# every new build
./devland/gke/deploy_app_to_gke_devland.sh

# faster only update app
# ./devland/gke/deploy_update_app_to_gke_devland.sh

kubectl get svc ${SERVICE_NAME} -o yaml