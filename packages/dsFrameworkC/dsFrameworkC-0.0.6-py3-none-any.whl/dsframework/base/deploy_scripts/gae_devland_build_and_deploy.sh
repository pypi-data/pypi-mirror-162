#!/bin/bash

./devland/build_and_register_image_in_devland.sh

# FOR Gae
./devland/gae/deploy-gae-devland.sh

gcloud builds list


#You can stream logs from the command line by running:
#> gcloud app logs tail -s $APP_NAME
#To view your application in the web browser run:
#> gcloud app browse -s $APP_NAME