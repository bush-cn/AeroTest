union {
	char d[4096]; /* aligned buffer */
	struct inotify_event e;
} buf;