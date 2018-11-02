# Redocker

Re-Docker is a very simple tool to enable restarting a running docker container with a new image.  There are other tools that will do this but most of them require slightly more setup.

To use redocker add it to your path and when you start a command that you will want to update later use `redocker run` instead of `docker run`.  Later run `redocker checkup` to check if there's a new docker image available and if so pull it, kill the running container and start fresh using the same `run` command from when it was first started.  That's it!


There are 4 commands supported by redocker. Any commands not listed here are forwarded to the docker command.
- run -- Same as 'docker run' but stores everything needed to restart the container from a new image
- checkup -- Checks all containers for an updated image and if one is available pulls it and re-runs the container from that.
- list -- Lists all containers managed by redocker
- forget -- remove 'name' from redocker's memory


## How to install:
- pip install docker  
- add redocker to your path

## FAQ
Q: Will files stored in the container filesystem be preserved?  
A: No. The the running container will be deleted and a new one started with the same arguments.

Q: If I run `redocker checkup` will it restart my container if no new image is available?  
A: Nope

Q: Can I 'checkup' a single container rather than all of them?  
A: Yes. If you provide an argument to checkup it will be treated as a regular expression and matched against the container names

Q: Should I use this to manage my huge cluster of super important containers?  
A: Probably not. You may want to look at docker compose or something.
