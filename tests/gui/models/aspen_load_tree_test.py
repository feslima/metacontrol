import os, tempfile, shutil, time
import win32com.client as win32


filepath = r"C:\Users\Felipe\Desktop\GUI\python\infill.bkp"

# create a temporary directory to place the bkp copy file in there
temp_directory = tempfile.mkdtemp(prefix='pwctmp')
tempfile.mkstemp()
# copy the file
temp_aspen_path = os.path.join(temp_directory, 'pwc_temp.bkp')
shutil.copy2(filepath, temp_aspen_path)
# attempt to connect
try:
    aspen = win32.Dispatch('Apwn.Document')
except:
    print('Dispatch failed!')
else:
    print('Dispatch Successful!')

try:
    aspen.InitFromArchive2(os.path.abspath(temp_aspen_path))
except:
    print("Init from archive failed!")
else:
    print("Init from archive sucessful")

print(aspen.Tree.FindNode(r"\Data\Streams").Name)

print(temp_directory)

while True:
    try:
        aspen.Close()
    except:
        print("Connection closed!")
        break


os.remove(temp_aspen_path)
print(os.listdir(temp_directory))

try:
    shutil.rmtree(temp_directory)
except WindowsError:
    time.sleep(5.0)
    shutil.rmtree(temp_directory)
