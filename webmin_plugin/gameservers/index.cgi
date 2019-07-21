#!/usr/bin/perl
# index.cgi
# Display a list of game servers and their status, with buttons for start
# and stop.
#
# TBD: It would be extra-nice to display (and support refresh of) status!

require './gameservers-lib.pl';
&foreign_require('init', 'init-lib.pl');

$style = '<style>.force_center {text-align: center; margin: auto}</style>';

&ui_print_header(undef, $text{'index_title'}, '', undef, 1, 1, undef, $style);

@header_cell_tags = ( 'align="left"', 'align="left"', 'align="center" class="force_center"', 'align="center" class="force_center"' );
@cell_tags = ( 'align="left"', 'align="left"', 'align="center"', 'align="center"' );

print &ui_columns_start([ $text{'scriptname_header'},
                          $text{'description_header'},
                          $text{'status_header'},
                          $text{'actions_header'} ], 100, 0, \@header_cell_tags);

foreach $server (sort keys %config) {
   if ($config{$server} == 1) {
      $valid = init::action_status($server);
      $status = '';
      if ($valid == 0) {
         $description = $text{'server_not_found'};
         $actions = '';
      } else {
         $init_filepath = init::action_filename($server);
         $description = &html_escape(init::init_description($init_filepath));
         if (init::action_running(init::action_filename($server)) == 1) {
            $status = 'X';
            $disable_start = 1;
            $disable_stop = 0;
         } else {
            $disable_start = 0;
            $disable_stop = 1;
         }
         $actions = &ui_form_start('action.cgi', 'post');
         $actions = $actions . &ui_hidden('server', $server);
         $actions = $actions . &ui_form_end([ [ 'start', $text{'start_button'}, undef, $disable_start ],
                                              [ 'stop', $text{'stop_button'}, undef, $disable_stop ],
                                              [ 'restart', $text{'restart_button'} ] ]);
      }
      print &ui_columns_row([ $server, $description, $status, $actions ], \@cell_tags);
   }
}

print &ui_columns_end();

print '<p/><p>'.$text{'status_note'}.'</p>';
