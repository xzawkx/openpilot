# Waifu theme by Tunder
## Installation

- cd /data/openpilot
- change "base" to "waifu" on first lines of selfdrive/ui/paint.cc and selfdrive/ui/sound.cc
- change boot animation
  - cd selfdrive/ui/themes/waifu
  - ./install_bootanim.sh
- optional: restore default boot animation
  - cd selfdrive/ui/themes/base
  - ./install_bootanim.sh

source: https://github.com/Tundergit/waifupilot
