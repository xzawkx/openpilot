# Install bootanimation

## Mac/PC
```
cd androd/platform-tools
adb root
adb remount
adb push bootanimation.zip /system/media/
```

## EON/C2
````
mount -o rw,remount /system
cp boot/bootanimation.zip /system/media/
mount -o ro,remount /system
````
