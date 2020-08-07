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

    if [ -f install_bootanim.sh ]; then
      echo "Installing boot animation"
      ./install_bootanim.sh
    fi

    echo "Patching ui"
    cd /data/openpilot
    if [ -f selfdrive/ui/themes/$1/diff/$1-theme.diff ]; then
      git apply selfdrive/ui/themes/$1/diff/$1-theme.diff
    else
      echo "selfdrive/ui/themes/$1/diff/$1-theme.diff not found"
    fi

    echo "Patching spinner"
    if [ -f selfdrive/ui/themes/$1/diff/$1-spinner.diff ]; then
      git apply selfdrive/ui/themes/$1/diff/$1-spinner.diff
      echo "Rebuilding spinner"
      cd selfdrive/ui/spinner
      make clean
      make
    else
      echo "Spinner patch not found"
    fi
    echo "Restarting to apply theme.."
    sleep 2
    reboot
  else
    echo "Theme $1 not found"
  fi
fi
