# satnogs2gr-satellites
<u>Dependencies</u>

Install SoundFile with 

<quote>sudo pip3 install SoundFile</quote>

Code to take the ogg file from gr-satnogs and pass it through gr-satellites

Create the folder: sudo mkdir /var/lib/satnogs/data

Put the following into the post-observation script textbox in satnogs-setup

/path/to/python /path/to/pythonscript/s2grs.py {{ID}} {{TLE}} {{TIMESTAMP}} {{SCRIPT_NAME}}

The resulting output will be put in the /var/lib/satnogs/data folder with the name output_XXXXX.txt where XXXXX is the NORAD ID of the satellite

The wav file required for gr-satellites will also be in the /var/lib/satnogs/data folder and should be removed once analysis is complete.
