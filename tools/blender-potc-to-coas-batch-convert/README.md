# Blender batch PotC to COAS conversion

Batch conversion of PotC to COAS using Artess999's *.gm import/export plugins for blender.    The python script needs to be run within blender for it to work (see below).


It requires two parameters to be specified the origin mod folder and the output_dir.    It reads the initModels.c and uses it to find and convert all male and 
female models.   You may need to massage that file a little for it to work.   I removed all double spaces or combinations of tab (\t) and space.  I also made sure that all indentations are tabs.


It requires the target folder to have the 'man_coas.ani' and 'woman_coas.ani' (not 100% sure).  


You need to add blender to your system path so that it can run from the command line on the location of the script.


The script creates a new initModels.c adding the COAS animation.


## Blender Usage
```
blender --background --python potc-coas-convert.py -- --nh_dir "D:/Maelstrom/games/new-horizons" --output_dir "D:/Maelstrom/games/new-horizons-convert"
```

## Author

[Quiet-Sun](https://github.com/amunozj)