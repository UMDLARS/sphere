import argparse
from elftools.elf.elffile import ELFFile

def debug_line(binary_file):
    lines_offsets = {}
    with open(binary_file, 'rb') as file:
        elffile = ELFFile(file)
        if not elffile.has_dwarf_info():
            print('  file has no DWARF info')
            return
        dwarfinfo = elffile.get_dwarf_info()
        for CU in dwarfinfo.iter_CUs():
            lines_program = []
            cu_die = CU.get_top_DIE()
            cu_name = cu_die.attributes['DW_AT_name'].value.decode()
            lines = dwarfinfo.line_program_for_CU(CU)
            debugsec_lines = lines.get_entries()
            for line in debugsec_lines:
                #print(line)
                if line.state is not None:
                    lines_program.append((line.state.line,hex(line.state.address)))
            lines_offsets[cu_name] = lines_program

    return lines_offsets

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('binary', help='path to binary folder')
    args = parser.parse_args()
    binary_file = args.binary
    lines_offsets = debug_line(binary_file)
    print(lines_offsets)
