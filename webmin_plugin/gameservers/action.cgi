#!/usr/bin/perl
# action.cgi
# Pass an action to the appropriate init script for a server.

require './gameservers-lib.pl';
&foreign_require('init', 'init-lib.pl');
&ReadParse();

$server = $in{'server'};

&ui_print_unbuffered_header(undef, "$server", '');

if ($in{'start'}) {
   ($ok, $out) = init::start_action($server);
} elsif ($in{'stop'}) {
   ($ok, $out) = init::stop_action($server);
} elsif ($in{'restart'}) {
   ($ok, $out) = init::restart_action($server);
} else {
   ($ok, $out) = (0, &text('bad_action', $action));
}

print "<pre>$out</pre>\n";

&ui_print_footer('', $text{'index_return'});
