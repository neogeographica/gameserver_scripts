#!/usr/bin/perl
# index.cgi
# Display a list of game servers and their status, with buttons for start
# and stop.
#
# TBD: It would be extra-nice to display (and support refresh of) status!

require './gameservers-lib.pl';
&foreign_require('init', 'init-lib.pl');

&ui_print_header(undef, $text{'index_title'}, '', undef, 1, 1);

print &ui_columns_start([ $text{'scriptname_header'},
                          $text{'description_header'},
                          $text{'actions_header'} ], 100, 0);

foreach $server (sort keys %config) {
   if ($config{$server} == 1) {
      $valid = init::action_status($server);
      if ($valid == 0) {
         $description = $text{'server_not_found'};
         $actions = '';
      } else {
         $init_filepath = init::action_filename($server);
         $description = &html_escape(init::init_description($init_filepath));
         $actions = &ui_form_start("action.cgi", "post");
         $actions = $actions . &ui_hidden("server", $server);
         $actions = $actions . &ui_form_end([ [ 'start', $text{'start_button'} ],
                                              [ 'stop', $text{'stop_button'} ],
                                              [ 'restart', $text{'restart_button'} ] ]);
      }
      print &ui_columns_row([ $server, $description, $actions ]);
   }
}

print &ui_columns_end();
