# obs-volumn-toggle-image
toggle image if higher than threshold

## How To Use
[GarrettGunnell](https://github.com/GarrettGunnell/obs-scripts) has already done a great tutorial.

Download [script](https://github.com/Artin0123/obs-volumn-toggle-image/blob/main/obs_vt.py) and import it.

## Why make this when there are already script available for use?

Because I made it before I found the script. (Yeah, a dump reason)  
But... it still has advantages!  
1. It's more lightweight and has a lower detection frequency in default. (assuming the user already has a blink animation source to improve performance)  
2. Similar to the first point, this code is easier to understand and configure.

## Variables

 - **G.tick**: how often script update (default = 0.3 seconds)  
 - **G.source_name**: audio source name (default = 擷取音訊輸出)  
 - **G.mouth_image_source_name**: image source name to toggle visibility (default = mouth)  
 - **G.scene_Name**: The name of the scene where the image source is located (default = Walling)  
 - **G.threshold**: dB value to toggle visibility (default = -30.0 dB)  
