# obs-volumn-toggle-image
toggle image if higher than threshold

**Demo**  

https://github.com/user-attachments/assets/0015629f-9577-48e9-a8ed-5a6ea0859913

## How To Use
[GarrettGunnell](https://github.com/GarrettGunnell/obs-scripts?tab=readme-ov-file#how-to-use) has already done a great tutorial.

Download [script](https://github.com/Artin0123/obs-volumn-toggle-image/blob/main/obs_vt.py) and import it.

## Why make this when there are already script available for use?

Because I made it before I found the script. (Yeah, a dump reason)  
But... it still has advantages!  
1. It's more lightweight and has a lower detection frequency in default. (assuming the user already has a blink animation source to improve performance)  
2. Similar to the first point, this code is easier to understand and configure.

## Variables

```
# how often script update (seconds)  
G.tick = 300

# audio source name  
G.source_name = "擷取音訊輸出"

# image source name to toggle visibility  
G.mouth_image_source_name = "mouth"

# The name of the scene where the image source is located  
G.scene_Name = "Walling"

# G.threshold: dB value to toggle visibility  
G.threshold = -30.0  
```
