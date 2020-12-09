# ACTV Competizione - Assetto Corsa TV

for Assetto Corsa

###Contains:
* Tower (standings - battles-realtime)
* Delta
* Driver info (driver info - qualification time - fastest lap)
* Timer (Session info)
* Weather (Track conditions)
* Config (Configuration)


###Changelog.
1.2.0.0
* Tower: bug fix blue names in qualy
* Tower: bug fix race start positions (progress)
* Tower/timer: bug fix pit window opens on first lap
* Tower: added tires(last stop), number of stops
* Tower: added class filters
* Tower: added current tires
* Tower: qualify sector mode
* Tower: display on race start
* Info: Removed sector mapping
* Info: info driver picture (how to set up in img/divers/readme.txt)
* Info: added flags in race (default AC flags or img/flags/readme.txt to set up custom)
* ui badge as logo, then AC logo
* onedrive and moved user folder support
* Optimisations : max refresh rate, aggregated redundant api calls
  
1.1.0.0
* Added configurable car/driver classes - rename car_classes.template.ini to car_classes.ini to get started, exemples inside the file
* Added weather/track conditions widget
* Delta - fixed current lap time / calculated delta for other cars
* Delta - import delta from other car (full lap needed, otherwise no button)
* Delta - Resize window from row height
* Delta - fix incorrect last lap after browsing others
* Delta - Timing out background and buttons, annoyance
* Delta - fixed finish flag only when driver has finished
* Tower - fixed name mode was changing at the end of the race
* Tower - realtime out laps marked in blue
* Tower - realtime more realistic gaps when no reference laps was done, specially on longer tracks
* Info - fix qualify/practice sector timing for all cars
* Info - Pit lane timer

1.0.0.0
* Initial release

###Installation instructions
Download the released package at Racedepartment
https://www.racedepartment.com/downloads/actv-competizione.35499/

1-extract the archive to your assettocorsa folder(...\Steam\steamapps\common\assettocorsa\)

2-In the game's main menu
  go to Options -> General
  in the section UI Modules
  check actv_competizione

3-In game all 5 widgets should appear in the list:
  ACTV CP Info, ACTV CP Timer, ACTV CP Tower, ACTV CP Delta and ACTV CP config
  -if you don't see them at first its normal if they have nothing to show but a mouse over the widget will trigger a background and a title(AC puts them at the top left by default) allowing you to place them as you want

4-breathe in, breathe out, don't forget to hydrate ;) you are all set

###Credits

Prunn

OV1 - base of classes

ACTV - base of the project

Fonts:

Open Sans Condensed : https://fonts.google.com/specimen/Open+Sans+Condensed

###License
This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.
GNU General Public License v3.