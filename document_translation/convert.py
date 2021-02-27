import multiprocessing
import time
import subprocess
import sys
import os
import time
import shutil

def convert2odt(file_path, save_path ):
    command = ['unoconv', '-o', save_path , '-f', 'odt', file_path] 
    # for the command to run: sudo apt install libreoffice
    code = subprocess.run(command)
    
def wait_sometime(file_path):
    """
    Returns:
        file_path: success
        'Operation Failed': Failure
    """
    cnt = 0
    while(True):
        if(os.path.isfile(file_path)):
            return file_path
        elif(cnt <= 7):
            time.sleep(1)
            cnt += 1
        else:
            return "Operation Failed"
    
def check_and_convert(file_path, save_path):    
    # Start conversion as a process
    p1 = multiprocessing.Process(target=convert2odt, args=(file_path, save_path))
    p1.start()
    p1.join(5)
    
    # Assumption that soffice is freezed
    if(p1.is_alive()):
        print("TRY 1: Process is alive....so kill - soffice.bin ...")
        subprocess.run(['sudo','killall', 'soffice.bin'])
        p1.terminate()

        # We are now confirm that soffice is not freezed
        p2 = multiprocessing.Process(target=convert2odt, args=(file_path, save_path))
        p2.start()
        p2.join(5)

        # Assumption that soffice is freezed
        if(p2.is_alive()):
            print("TRY 2: Process is alive....so kill - soffice.bin...")
            print("Input file is broken or unable to convert to odt... so exit the python program")
            subprocess.run(['sudo','killall', 'soffice.bin'])
            p2.terminate()
            sys.exit(1)
        else:
            print("If odt input --> unoconv is not feezed \n Else - File got successfully converted to odt through p2")
    else:
         print("If odt input --> unoconv is not feezed \n Else - File got successfully converted to odt through p1")   
            
# case 1: unoconv is freeze and txt is input --> done
# case 2: unoconv is not-freeze and txt is input --> done
# case 3: unoconv is freeze and broken input --> done
# case 4: unoconv is not-freeze and borken input --> done

def run_conversion(file_path, save_path):
    name = file_path.split('/')[-1]
    true_name = name.rsplit('.', 1)[0]  # file_name without file_path 
    print(name, true_name)
    output_type = name.split('.')[-1] # output type (pdf,docx,odt,etc) of the input file
    
    odt_name = true_name+'.odt'
    odt_file_path = os.path.join(save_path, odt_name)
    print(odt_file_path)
    
    if(output_type != 'odt'):
        check_and_convert(file_path, odt_file_path)
        temp_path = wait_sometime(odt_file_path)
        print(temp_path, '\n\n')
    else:
        check_and_convert('no_such_file', 'no_such_file')
        shutil.copy2(file_path, odt_file_path)
        temp_path = wait_sometime(odt_file_path)
        print(temp_path, '\n\n')
    return odt_file_path
        