# lifewatcher

COEN6313

### Web Development (Manager System)

### Mobile App Development (Cross-platform)

### Cloud Service Development (RESTful API)

### Core  Function Development (vision detection)

How to come into VM:
- vagrant up  ==> start up ur VM
- vagrant status ==> check the status of ur VM
- vagrant ssh [ur VM name]==> come into ur VM
- exit ==> exit ur VM
- vagrant halt ==> power off ur VM

using .venv when u use python:
- in devmachine(VM):
    - cd /vagrant/
    - source .venv/bin/activate ==> can come into the python virtual environment
    - deactivate  ==> can exit the virtual environment
###
'''
docker build . -t lifewatcher
'''
#### use our dockerFile to build a images

'''
docker run lifewatcher
docker run -d -p 80:80 lifewatcher
docker status
docker start xxx(id of ur container)
'''
#### use our image to build a conatiner 

'''
docker exec -it xxx sh
'''
#### come into the container

In container: mkdir /Downloads 
And in containe: mkdir /Downloads/images

In container(manually): python LifeWatcher_Web.py 
Test: in container: curl -i http://0.0.0.0:80/
