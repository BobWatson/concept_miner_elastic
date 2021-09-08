# Concept Miner Elastic

A framework around prodigy to let end users start and stop the interface, trigger training, etc. - for small group collab.

## Installation

1. Make sure you have an active [prodigy](https://prodi.gy/) license, and can run VS Code dev containers
2. Place the repository files in a folder
3. Download *prodigy-1.11.2-cp39-cp39-linux_x86_64.whl* from prodigy and place in the build/prodigy directory.
4. Open the folder in VSCode and '[Reopen in Container](https://code.visualstudio.com/docs/remote/containers)'
5. Create ./conf/app.conf from ./conf/app.dist.conf and update with your labels
6. Once built, run 'python /workspace/app/app.py' from the container (or launch from VS Code)
7. The server should now be running on http://127.0.0.1:8000/ (you can change this port in ./conf/nginx.conf)

## Usage

1. Visit http://<your_ip>:8000/
2. From the Home tab, upload your PDF or TXT documents for training
3. Navigate to the Annotating tab, and perform your prodigy annotations
4. Once you have completed a number of annotations, return to 'Home' and click 'Go' next to 'Stop annotating (Start training)'
5. Results will be on the 'Training Log' tab, and your model and annotations will be in the ./output folder (or as configured in app.conf)
