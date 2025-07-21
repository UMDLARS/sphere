from elftools.elf.elffile import ELFFile

filename = 'path to binary'
with open(filename, 'rb') as file:
    elffile = ELFFile(file)
    elf_type = elffile.header.e_type
    print(elf_type)
