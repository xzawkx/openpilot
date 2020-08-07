# Experimental Openpilot UI themes

Themes allow changing openpilot UI
- fonts
- colors
- images
- sounds
- spinner
- boot animation

spinner and actual theme switching (ui/paint.cc and ui/sound.cc) require `git diff` files

## List of themes
- base - openpilot stock theme
- waifu - anime-inspired theme by Tunder

## Switching to a new theme

```
cd /data/openpilot/selfdrive/ui/themes
./switch-theme.sh
```

## Create a new theme

```
cd /data/openpilot
cd selfdrive/ui/themes
cp -a base new_theme
```
