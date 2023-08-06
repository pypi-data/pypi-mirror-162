## qcheck

A script to display user quota info graphically on the terminal


This is just a wrapper script around quota -a, therefore quota should be installed and users should have access to it

```bash
Storage space report for user's account:
     storage: |==============                     | 40%,  393MB used,  583MB free
  file count: |===========                        | 34%, 6822Used,    13178Free
```


## Install and build locally

```bash
git clone $repo
pip3 install build
apt install python3-virtualenv

cd $repo
python3 -m build 
pip3 install dist/qcheck...*...whl
```


## Cool use cases

You can have qcheck run on login for a user by placing the following in `/etc/profile.d/motd.sh`

```
/usr/local/bin/qcheck $USER
```
