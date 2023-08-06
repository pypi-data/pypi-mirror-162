#ifdef __cplusplus

#include "minunit.h"

node_t THE_FIRST(nullptr);
node_t* FIRST = nullptr;
node_t* LAST = nullptr;

node_t::node_t(suite_ptr _suite) {
	// Translation unit hack...don't want to override tests by different translation units.
	if (FIRST == nullptr){
		FIRST = &THE_FIRST;
		LAST = FIRST;
	}
	if (_suite != nullptr){
		next = 0;
		ptr_toSuite = _suite;
		LAST->next = this;
		LAST = this;
	}
}

/*  Misc. counters */
int minunit_run = 0;
int minunit_assert = 0;
int minunit_fail = 0;
int minunit_status = 0;

/*  Timers */
double minunit_real_timer = 0;
double minunit_proc_timer = 0;

/*  Last message */
char minunit_last_message[MINUNIT_MESSAGE_LEN];

#endif