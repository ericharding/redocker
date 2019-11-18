#!/usr/bin/python
import docker, sys, os, json
from subprocess import call

def config_path():
    dir = os.path.expanduser('~/.redocker')
    if not os.path.exists(dir): os.makedirs(dir)
    config_file = os.path.join(dir, "config.json")
    return config_file

def load_config():
    config_file = config_path()
    default = dict(cmds={})
    if os.path.exists(config_file):
        with open(config_file, 'r') as fp:
            try:
                data = json.load(fp)
            except:
                return default
            return data
    else:
        return default
    
def save_config(data):
    config_file = config_path()
    with open(config_file, 'w') as fp:
        json.dump(data, fp)

def find_image(images, name):
    # kind of a hack here
    for image in images:
        for tag in image.tags:
            tagName = tag.split(':')[0]
            if tagName == name or tag == name:
                return image
    return None

# !
def run(args):
    client = docker.from_env()
    # list all images
    all_images = client.images.list()
    image_name = ""
    for a in args:
        if find_image(all_images, a) != None:
            image_name = a
    # If we can't determine image name give up
    print "image name: ", image_name
    if image_name == "":
        print "Can't determine image name. Please 'docker pull' before running"
        return
    # get container name
    name = ""
    for i in range(0,len(args)):
        if args[i] == '--name': name = args[i+1]
    if name == "":
        print "Please provide a name for this container using the --name argument"
        return
    if not '-d' in args:
        print "Did you mean to include -d to detach from this image?"
        print "Or perhaps you meant 'docker' instead of 'redocker'"
        return
    # record the command
    config = load_config()
    config['cmds'][name] = dict(name = name, image = image_name, command = args)
    save_config(config)
    x = call(['docker', 'run'] + args)

def checkup_one(client, container, args):
    # pull image
    cur_image = container.image
    tag = cur_image.tags[0].split(':')[0]
    print "current image:", cur_image.short_id
    new_image = client.images.pull(tag+":latest")
    print "new image:", new_image.short_id
    # see if it has changed
    if new_image.id == cur_image.id:
        print "No change"
        return
    print "Changed!"
    # if changed stop and remove old container
    container.stop()
    container.remove()
    # start new container
    print "Restarting..."
    x = call(['docker', 'run'] + args)

# !
def checkup(args):
    import re
    client = docker.from_env()
    config = load_config()
    pattern = ".*"
    if len(args) == 1: pattern = args[0]
    for cmd in config['cmds'].values():
        if re.search(pattern, cmd['name']) != None:
            print "checking '{0}'...".format(cmd['name'])
            container = client.containers.get(cmd['name'])
            checkup_one(client, container, cmd['command'])

def print_args(args):
    import re
    config = load_config()
    pattern = ".*"
    if len(args) == 1: pattern = args[0]
    for cmd in config['cmds'].values():
        if re.search(pattern, cmd['name']) != None:
            command = " ".join(cmd['command'])
            print "docker run ", command

def list():
    config = load_config()
    for cmd in config['cmds'].values():
        print "{0}:\n  image: {1}\n  args: {2}".format(cmd['name'], cmd['image'], ' '.join(cmd['command']))

def forget(args):
    config = load_config()
    for x in args:
        if x in  config['cmds']:
            config['cmds'].pop(x)
    save_config(config)

def purge():
    client = docker.from_env()
    for a in client.images.list():
        if len(a.tags) == 0:
            print "cleaning up ...", a.short_id
            client.images.remove(a.id)

def showhelp():
    print "RE-docker"
    print "Runs docker images in a restartable way."
    print "\trun [args] \t-- Same as 'docker run' but stores everything needed to restart the container from a new image"
    print "\tcheckup \t-- Checks all containers for an updated image and if one is available pulls it and re-runs the container from that."
    print "\tlist \t\t-- Lists all containers managed by redocker"
    print "\tforget [name] \t-- remove 'name' from redocker's memory"
    print "\tpurge \t\t-- Clean up all docker images with no tag"
    print "CAVETS:" 
    print "\t1) you must provide a --name"
    print "\t2) You must 'docker pull' before running"
    print "\t3) You must use the :latest tag (or no tag)"

def other(cmd, args):
    call(['docker', cmd] + args)


if len(sys.argv) < 1:
    showhelp()
else:
    arg = sys.argv[1]
    rest = sys.argv[2:]
    if arg == 'run': run(rest)
    elif arg == 'checkup': checkup(rest)
    elif arg == 'print': print_args(rest)
    elif arg == 'list': list()
    elif arg == 'forget': forget(rest)
    elif arg == 'help': showhelp()
    elif arg == 'purge': purge()
    else: other(arg, rest)
