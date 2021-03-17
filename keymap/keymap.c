#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/select.h>
#include <inttypes.h>
#include <sys/ioctl.h>
#include "linux-input.h"


#define ev_name(code)  ((code) < EV_MAX  && EV_NAME[code]  ? EV_NAME[code]  : "???")
#define ev_type_name(type, code) ((code) < EV_TYPE_MAX[type] && EV_TYPE_NAME[type][code] ? EV_TYPE_NAME[type][code] : "???")
#define BITFIELD uint32_t

int device_open(int nr, int verbose);

extern char *EV_NAME[EV_CNT];
extern int EV_TYPE_MAX[EV_CNT];
extern char **EV_TYPE_NAME[EV_CNT];
extern char *BUS_NAME[];

static __inline__ int test_bit(int nr, BITFIELD * addr)
{
        BITFIELD mask;

        addr += nr >> 5;
        mask = 1 << (nr & 0x1f);
        return ((mask & *addr) != 0);
}




char *EV_NAME[EV_CNT] = {
#include "EV.h"
};
static char *REL_NAME[REL_CNT] = {
#include "REL.h"
};
static char *ABS_NAME[ABS_CNT] = {
#include "ABS.h"
};
static char *MSC_NAME[MSC_CNT] = {
#include "MSC.h"
};
static char *LED_NAME[LED_CNT] = {
#include "LED.h"
};
static char *SND_NAME[SND_CNT] = {
#include "SND.h"
};
#ifndef REP_CNT
#define REP_CNT (REP_MAX + 1)
#endif
static char *REP_NAME[REP_CNT] = {
#include "REP.h"
};
static char *KEY_NAME[KEY_CNT] = {
#include "KEY.h"
#include "BTN.h"
};
static char *SW_NAME[SW_CNT] = {
#include "SW.h"
};


int EV_TYPE_MAX[EV_CNT] = {
        [EV_REL] = REL_MAX,
        [EV_ABS] = ABS_MAX,
        [EV_MSC] = MSC_MAX,
        [EV_LED] = LED_MAX,
        [EV_SND] = SND_MAX,
        [EV_REP] = REP_MAX,
        [EV_KEY] = KEY_MAX,
        [EV_SW] = SW_MAX,
};

char **EV_TYPE_NAME[EV_CNT] = {
        [EV_REL] = REL_NAME,
        [EV_ABS] = ABS_NAME,
        [EV_MSC] = MSC_NAME,
        [EV_LED] = LED_NAME,
        [EV_SND] = SND_NAME,
        [EV_REP] = REP_NAME,
        [EV_KEY] = KEY_NAME,
        [EV_SW] = SW_NAME,
};

char *BUS_NAME[] = {
#include "BUS.h"
};


struct input_keymap_entry_v2 {
#define KEYMAP_BY_INDEX	(1 << 0)
	uint8_t  flags;
	uint8_t  len;
	uint16_t index;
	uint32_t keycode;
	uint8_t  scancode[32];
};

#ifndef EVIOCGKEYCODE_V2
#define EVIOCGKEYCODE_V2 _IOR('E', 0x04, struct input_keymap_entry_v2)
#endif

struct kbd_entry {
	unsigned int scancode;
	unsigned int keycode;
};

struct kbd_map {
	struct kbd_entry  *map;
	int               keys;
	int               size;
	int               alloc;
};


int device_open(int nr, int verbose)
{
        char filename[32];
        int fd;

        snprintf(filename,sizeof(filename),"/dev/input/event%d",nr);
        fd = open(filename,O_RDONLY);
        if (-1 == fd) {
                fprintf(stderr,"open %s: %s\n",
                        filename,strerror(errno));
                return -1;
        }
        //if (verbose) fprintf(stderr,"%s\n",filename);

        return fd;
}


static struct kbd_map* kbd_map_read(int fd, unsigned int version)
{
	struct kbd_entry entry;
	struct kbd_map *map;
	int rc;

	map = malloc(sizeof(*map));
	memset(map,0,sizeof(*map));
	for (map->size = 0; map->size < 65536; map->size++) {
		if (version < 0x10001) {
			entry.scancode = map->size;
			entry.keycode  = KEY_RESERVED;
			rc = ioctl(fd, EVIOCGKEYCODE, &entry);
			if (rc < 0) {
				map->size--;
				break;
			}
		} else {
			struct input_keymap_entry_v2 ke = {
				.index = map->size,
				.flags = KEYMAP_BY_INDEX,
				.len = sizeof(uint32_t),
				.keycode = KEY_RESERVED,
			};

			rc = ioctl(fd, EVIOCGKEYCODE_V2, &ke);
			if (rc < 0)
				break;
			memcpy(&entry.scancode, ke.scancode,
				sizeof(entry.scancode));
			entry.keycode = ke.keycode;
		}

		if (map->size >= map->alloc) {
			map->alloc += 64;
			map->map = realloc(map->map, map->alloc * sizeof(entry));
		}

		map->map[map->size] = entry;

		if (KEY_RESERVED != entry.keycode)
			map->keys++;
	}
	if (map->keys) {
		//fprintf(stderr,"map: %d keys, size: %d/%d\n",	map->keys, map->size, map->alloc);
		return map;
	} else {
		free(map);
		return NULL;
	}
}

/*
static int kbd_map_write(int fh, struct kbd_map *map)
{
	int i,rc;

	for (i = 0; i < map->size; i++) {
		rc = ioctl(fh, EVIOCSKEYCODE, &map->map[i]);
		if (0 != rc) {
			//fprintf(stderr,"ioctl EVIOCSKEYCODE(%d,%d): %s\n",map->map[i].scancode,map->map[i].keycode,strerror(errno));
			return -1;
		}
	}
	return 0;
}
*/

static void kbd_key_print(FILE *fp, int scancode, int keycode)
{
char keyname[100], sub[94];
char key[4] = "KEY_";
int length, c = 0;

strcpy(keyname , ev_type_name(EV_KEY, keycode));

length = strlen(keyname) - 4;

if (strncmp(keyname, key, 4) == 0)

 {

while (c < length) {
      sub[c] = keyname[4+c];
      c++;
   }
   sub[c] = '\0';
   strcpy(keyname, sub);
 }

	fprintf(stdout, "%d:%s\n", keycode, keyname);
}

static void kbd_map_print(FILE *fp, struct kbd_map *map, int complete)
{
	int i;

	for (i = 0; i < map->size; i++) {
		if (!complete  &&  KEY_RESERVED == map->map[i].keycode)
			continue;
		kbd_key_print(fp,map->map[i].scancode,map->map[i].keycode);
	}
}
/*
static int kbd_map_parse(FILE *fp, struct kbd_map *map)
{
	struct kbd_entry entry;
	char line[80],scancode[80],keycode[80];
	int i;

	while (NULL != fgets(line,sizeof(line),fp)) {
		if (2 != sscanf(line," %80s = %80s", scancode, keycode)) {
			fprintf(stderr,"parse error: %s",line);
			return -1;
		}

		// parse scancode 
		if (0 == strncasecmp(scancode,"0x",2)) {
			entry.scancode = strtol(scancode, NULL, 16);
		} else {
			entry.scancode = strtol(scancode, NULL, 10);
		}
		if (entry.scancode <  0 ||
		    entry.scancode >= map->size) {
			fprintf(stderr,"scancode %d out of range (0-%d)\n",entry.scancode,map->size);
			return -1;
		}

		// parse keycode 
		for (i = 0; i < KEY_MAX; i++) {
			if (!EV_TYPE_NAME[EV_KEY][i])
				continue;
			if (0 == strcmp(keycode,EV_TYPE_NAME[EV_KEY][i]))
				break;
		}
		if (i == KEY_MAX)
			entry.keycode = atoi(keycode);
		else
			entry.keycode = i;

		fprintf(stderr,"set: ");
		kbd_key_print(stderr,entry.scancode,entry.keycode);
		map->map[entry.scancode] = entry;
	}
	return 0;
}
*/

static void kbd_print_bits(int fd)
{
char keyname[100], sub[94];
char key[4] = "KEY_";
int length, c = 0;

	BITFIELD bits[KEY_CNT/sizeof(BITFIELD)];
	int rc,bit;

	rc = ioctl(fd,EVIOCGBIT(EV_KEY,sizeof(bits)),bits);
	if (rc < 0)
		return;
	for (bit = 0; bit < rc*8 && bit < KEY_MAX; bit++) {
		if (!test_bit(bit,bits))
			continue;
		if (EV_TYPE_NAME[EV_KEY][bit]) {

                strcpy(keyname , EV_TYPE_NAME[EV_KEY][bit]);
                length = strlen(keyname) - 4;
                if (strncmp(keyname, key, 4) == 0)
                 {
                   while (c < length) {
                   sub[c] = keyname[4+c];
                   c++;
                 }
                 sub[c] = '\0';
                 c = 0;
                 strcpy(keyname, sub);
                 }
                  fprintf(stdout,"%d:%s\n", bit,keyname);
		} //else {fprintf(stderr,"%d:UNKNOWN\n", bit);	}
	}
}

static void show_kbd(int fd, unsigned int protocol_version)
{
	struct kbd_map *map;

	//device_info(fd);

	map = kbd_map_read(fd, protocol_version);
	if (map)
		kbd_map_print(stdout, map, 0);
	else
		kbd_print_bits(fd);
}
/*
static int set_kbd(int fd, unsigned int protocol_version, char *mapfile)
{
	struct kbd_map *map;
	FILE *fp;

	map = kbd_map_read(fd, protocol_version);
	if (NULL == map) {
		fprintf(stderr,"device has no map\n");
		close(fd);
		return -1;
	}

	if (0 == strcmp(mapfile,"-"))
		fp = stdin;
	else {
		fp = fopen(mapfile,"r");
		if (NULL == fp) {
			fprintf(stderr,"open %s: %s\n",mapfile,strerror(errno));
			close(fd);
			return -1;
		}
	}

	if (0 != kbd_map_parse(fp,map) ||
	    0 != kbd_map_write(fd,map)) {
		return -1;
	}

	return 0;
}
*/

int main(int argc, char *argv[])
{
	int  devnr, fd;
	//char *mapfile = NULL;
	unsigned int protocol_version;
	int rc = EXIT_FAILURE;

	devnr = atoi(argv[1]);

	fd = device_open(devnr, 1);

	if (fd < 0)
		goto out;

	if (ioctl(fd, EVIOCGVERSION, &protocol_version) < 0) {
		fprintf(stderr,
			"Unable to query evdev protocol version: %s\n",
			strerror(errno));
		goto out_close;
	}

	//if (mapfile)
	//	set_kbd(fd, protocol_version, mapfile);
	//else
	show_kbd(fd, protocol_version);

	rc = EXIT_SUCCESS;

out_close:
	close(fd);
out:
	return rc;
}

