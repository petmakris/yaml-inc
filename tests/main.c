#define HELLOWORLD 1


// --templater:nextline(FLAG1)
typedef struct phony { int x; } phony_struct;

// --templater:inject(FLAG2)


// --templater:begin(FLAG3)
int x = 0;
// --templater:end(FLAG3)

// --templater:inject(FLAG5)

int main(int argc, char ** argcv) {
    main(0, 0);
	return 0;
}

#endif
