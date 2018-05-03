#!/bin/bash

# abort on first command that fails
set -e

# did user pass in his credentials?
if [ -z "$X_NAME" ] || [ -z "$X_GID" ] || [ -z "$X_UID" ]; then
    echo 'ERROR: run me like this for proper user initialization:'
    echo ' docker run -e X_UID="$(id -u)" -e X_GID="$(id -g)" -e X_NAME="$(whoami)" -it -v $PWD:/somewhere --name test bla:latest --rm ...'
    exit 1
fi

# have we run before?
if [ -d "/home/$X_NAME" ]; then
  if [ -z "$@" ]; then
    echo "welcome back!"
  fi
else
  if [ -z "$@" ]; then
    echo "initializing /home/$X_NAME"
  fi

  groupadd -f -g $X_GID $X_NAME
  useradd -m $X_NAME -u $X_UID -g $X_GID

  echo "$X_NAME ALL=(ALL) ALL" >>/etc/sudoers
  echo "Defaults  lecture = never" >>/etc/sudoers

  passwd -q -d root
  passwd -q -d $X_NAME

  # make 'gateway' point to docker host IP
  ip r | awk '/^def/{print $3}' |tr -d '\n' >>/etc/hosts; echo "     gateway" >>/etc/hosts;

  cat /patch.bashrc >>/root/.bashrc
  cat /patch.bashrc >>/home/$X_NAME/.bashrc
fi

# switch to user and never come back
# if arguments are available, execute them immediately
if [ -z "$@" ]; then
  exec sudo -i -H -u $X_NAME /bin/bash
else
  exec sudo    -H -u $X_NAME /bin/bash -c "$@"
fi
