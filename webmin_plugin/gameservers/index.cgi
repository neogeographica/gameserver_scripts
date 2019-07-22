#!/usr/bin/perl
# index.cgi
# Display a list of game servers and their status, with buttons for start
# and stop.

require './gameservers-lib.pl';
&foreign_require('init', 'init-lib.pl');

$style = '<style>.force_center {text-align: center; margin: auto}</style>';

&ui_print_header(undef, $text{'index_title'}, '', undef, 1, 1, undef, $style);

@header_cell_tags = ( 'align="left"', 'align="left"', 'align="center" class="force_center"', 'align="center" class="force_center"' );
@cell_tags = ( 'align="left"', 'align="left"', 'align="center"', 'align="center"' );

print &ui_columns_start([ $text{'scriptname_header'},
                          $text{'description_header'},
                          $text{'port_header'},
                          $text{'actions_header'} ], 100, 0, \@header_cell_tags);

foreach $server (sort keys %config) {
   if ($config{$server} == 1) {
      $valid = init::action_status($server);
      if ($valid == 0) {
         $description = $text{'server_not_found'};
         $actions = '';
         $port = '';
      } else {
         $init_filepath = init::action_filename($server);
         $description = &html_escape(init::init_description($init_filepath));
         $port = &backquote_command($init_filepath . " port");
         if ($port != '') {
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
      print &ui_columns_row([ $server, $description, $port, $actions ], \@cell_tags);
   }
}

print &ui_columns_end();

print '<p/><p>' . $text{'status_note'} . '</p>';
