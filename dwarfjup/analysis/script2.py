import argparse
from elftools.elf.elffile import ELFFile

# this is a modification of code in this repository 

def extract_function(binary):

    with open(binary, 'rb') as f:

        elffile = ELFFile(f)
        # check if binary has dwarf information
        if not elffile.has_dwarf_info():
            print('  file has no DWARF info')
            return

        # extract the dwarf information
        dwarfinfo = elffile.get_dwarf_info()
        dies_CU = []
        for CU in dwarfinfo.iter_CUs():

            print('  Found a compile unit at offset %s, length %s' % (
                CU.cu_offset, CU['unit_length']))

           
            top_DIE = CU.get_top_DIE()
            
            list_dies_cu = []
            die_info_rec(top_DIE, list_dies_cu)
            # list of dwarf tree for each CU
            dies_CU.append(list_dies_cu)
        return dies_CU

def die_info_rec( die, list_dies_cu):
    list_dies_cu.append(die)
    for child in die.iter_children():
        die_info_rec(child, list_dies_cu)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('binary', help='path to binary folder')
    args = parser.parse_args()
    binary_file = args.binary
    CU_dies = extract_function(binary_file)
    
    for dies in CU_dies:
        for die in dies:
            if die.tag == 'DW_TAG_subprogram':
                print(die.attributes['DW_AT_name'].value.decode())


                


    


    
