# Concept Miner Elastic

A framework around prodigy to let end users start and stop the interface, trigger training, etc. - for small group collab.

## Installation

1. Make sure you have an active [prodigy](https://prodi.gy/) license
2. Create a .env file in the build directory (or edit docker-compose.yml in that location), containing:

    ```shell
    COMPOSE_PROJECT_NAME=concept_miner_elastic
    KIBANA_SERVER_PUBLICBASEURL=https://<your_base_url>/kibana
    TZ=<your_timezone>
    DEBUG=false
    PRODIGY_KEY=<your_prodigy_key>
    ```
3. Run `docker compose up`
8. The server should now be running on http://127.0.0.1:8000/ (you can change this port in ./conf/nginx.conf)

## Usage

1. Visit http://<your_ip>:8000/
2. From the Home tab, upload your PDF or TXT documents for training
3. Navigate to the Annotating tab, and perform your prodigy annotations
4. Once you have completed a number of annotations, return to 'Home' and click 'Go' next to 'Stop annotating (Start training)'
5. Results will be on the 'Training Log' tab, and your model and annotations will be in the ./output folder (or as configured in app.conf)
