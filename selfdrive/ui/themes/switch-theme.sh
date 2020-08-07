#!/usr/bin/bash

git reset --hard HEAD

cd /data/openpilot/selfdrive/ui/themes
 
if [ "$1" == "base" ]; then
  echo "Restoring base theme"
  cd base
  echo "Restoring boot animation"
  ./install_bootanim.sh
  echo "Restoring spinner"
  cd ../../spinner
  make clean
  make
  echo "Restarting to apply changes"
  sleep 2
  reboot
else
  if [ -d "$1" ]; then
    echo "Switching to theme: $1"
    cd "$1"
    if [ -f diff/$1-theme.diff ]; then
      git apply diff/$1-theme.diff
    else
      echo "diff/$1-theme.diff not found. Exiting"
      exit
    fi
    if [ -f install_bootanim.sh ]; then
      echo "Installing boot animation"
      ./install_bootanim.sh
    fi
    echo "Patching spinner"
    if [ -f diff/$1-spinner.diff ]; then
      git apply diff/$1-spinner.diff
      echo "Rebuilding spinner"
      cd ../../spinner
      make clean
      make
    else
      echo "Spinner patch not found"
    fi
    echo "Restarting to apply changes"
    sleep 2
    reboot
  else
    echo "Theme $1 not found"
  fi
fi
