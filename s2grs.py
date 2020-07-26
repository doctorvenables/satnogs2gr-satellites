#!/usr/bin/python3
import sys
import json
import os, shutil
import soundfile as sf
import subprocess
import datetime

def concat_params(*list):
  exec_list=[]
  null_list_element=[]
  for x in list:
    print(x)

    if (x != null_list_element):
      exec_list=exec_list+[x]
      print(exec_list)
  return exec_list
#Running gr-satellites as a sub-process in user satnogs environment
#Appears to need PYTHONPATH explicitly stated 
os.environ['PYTHONPATH'] = '/usr/local/lib/python3/dist-packages/'

print("Entering Python script to invoke gr-satellites")
script_name = sys.argv[4]
print("Name of script: ",script_name)
#satnogs bpsk observations require an offset of 12e3
if ('bpsk' in script_name):
     f_offset='--f_offset=12e3'
else:
     f_offset=''
#print("f_offset: ",f_offset)

print("Timestamp: ",sys.argv[3])

tle_data=json.loads(sys.argv[2])
sat_name_line=tle_data["tle0"]
sat_name=sat_name_line.split(" ")[0]
tle_second_line=tle_data["tle2"]

norad_id=tle_second_line.split(" ")[1]
print("Norad ID=",norad_id)

in_path = '/tmp/.satnogs/'
out_path = '/var/lib/satnogs/'

#Lists all files in temporary satnogs data directory
#This could be stripped down if you know your inpath is otherwise empty

for root, directories, files in os.walk(in_path, topdown=False):
    for name in files:
        fullname = os.path.join(root, name)
        if "out" in fullname:

#.out is the output file extension for ogg files from gr-satnogs

           newname = fullname.replace(".out",".ogg")
           shutil.copy(fullname, newname)

#Copy the .out to a file with the same name but a .ogg extesion
           out_newname = newname.replace(in_path,out_path)
           shutil.copy(newname,out_newname)
           os.remove(newname)
#Set name of output wav file
           wav_name= out_newname.replace(".ogg",".wav")
#Use sox to convert .ogg to .wav
convert_string=["/usr/bin/sox",out_newname,wav_name]
subprocess.run(convert_string)

#Remove the ogg file from /var/lib
os.remove(out_newname)

print("Starting gr-satellites processing for ",sat_name)

#Set up arguments for gr_satellites

wav_arg="--wavfile="+wav_name
exec_string= '/usr/local/bin/gr_satellites'
now_kss=datetime.datetime.now()
kiss_arg="--kiss_out="+out_path+'/data/'+str(norad_id)+'kiss_'+now_kss.strftime("%Y-%m-%d-%H-%M-%S")+'.kss'
samp_rate="--samp_rate=48e3"
clk_limit="--clk_limit=0.03"
#exec_arg0=[exec_string,str(norad_id),wav_arg,"--samp_rate=48e3","--clk_limit=0.03",kiss_arg]
print('Kiss arg=',kiss_arg)
#satnogs bpsk observations require an offset of 12e3
#if ('bpsk' in script_name):
#     exec_arg0=[exec_string,str(norad_id),wav_arg,"--samp_rate=48e3","--clk_limit=0.03","--f_offset=12e3",kiss_arg]
exec_arg0=concat_params(exec_string,str(norad_id),wav_arg,samp_rate,clk_limit,kiss_arg,f_offset)
print(exec_arg0)

#Run gr_satellites
result = subprocess.run(exec_arg0,capture_output=True,text=True)

#Prints output and errors to terminal (which for gr-satnogs is captured in journal
#This out can be seen with journalctl | grep -A 50 script which points to the start of the output for this script.
print("Output: ",result.stdout)
print("STDERR: ",result.stderr)

#Prints results of telemetry output to txt file called output_NNNNN.txt where NNNNN is the NORAD ID of the sat

output_txt_file=out_path+'/data/output_'+str(norad_id)+'.txt'
print("Output txt file:",output_txt_file)

#"a" ensures that data is appended to the end of the file, keeping all output for one sat in same file.
file1 = open(output_txt_file,"a")
now = datetime.datetime.now()
print ("Current date and time : ", now.strftime("%Y-%m-%d %H:%M:%S"))
date_stamp="Current date and time : "+ now.strftime("%Y-%m-%d %H:%M:%S")
file1.write(date_stamp)
file1.write(result.stdout)
file1.close()
