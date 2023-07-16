#include <assignment2.h>

int32_t main(int32_t argc, char *argv[])
{
	int32_t fd; //file descriptor

	if(argc!=2) {
		printf("Usage: editro <file>\n");
		return 0;
	}

	fd = open(argv[1], O_RDWR|O_SYNC); //open the first argument(expected ELF file) with read and write mode
	if(fd<0) {
		printf("Error %d Unable to open %s\n", fd, argv[1]);
		return 0;
	}

	Elf64_Ehdr ehdr;
	Elf64_Shdr* sh_tbl;
	
	read_elf_header(fd, &ehdr); // allocate the memeory of variable 'fd' as much as size of ELF header to variable 'ehdr' whose type of ELF header
	
    if(!is_elf( ehdr )) {
		printf("ELF File: FALSE\n");
		return 0;
	}

	printf("ELF File: TRUE\n");
	
	print_elf_header(ehdr);

	sh_tbl = malloc(ehdr.e_shentsize * ehdr.e_shnum); //e_shentsize : section header entry size, e_shnum: number of section header table entry
	if(!sh_tbl) {
		printf("Failed to allocate %d bytes\n", (ehdr.e_shentsize * ehdr.e_shnum));
	}

	print_section_headers(fd, ehdr, sh_tbl);

	Section_Info* rodata_info = (Section_Info *)malloc(sizeof(Section_Info));

	rodata_info = find_rodata_info(fd, ehdr, sh_tbl);
	char* data = malloc(rodata_info->sh_size);
	lseek(fd, rodata_info->sh_offset, SEEK_SET);
	read(fd, data, rodata_info->sh_size);

	find_and_change_difficult(fd, data, rodata_info->sh_offset, rodata_info->sh_size);

	return 0;

}

