# recursive, permissions, times
rsync -rpt -v --delete-after \
    --exclude="__pycache__/" \
    --exclude="/.git/" \
    --exclude="/main.build/" \
    --exclude="/main.bin" \
    --exclude="/.idea/" \
    --exclude="/keymap/keymap" \
    --exclude="/keymap/keymap.o" \
    --exclude="/qml/" \
    --exclude="/settings.ini" \
    --exclude="/properties_export.html" \
    ./ pi@SHPI:/home/pi/main_app_dev/
