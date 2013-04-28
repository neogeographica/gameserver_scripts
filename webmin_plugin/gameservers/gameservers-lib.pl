=head1 gameservers-lib.pl

Common code for managing game servers controlled through init scripts.
=cut

BEGIN { push(@INC, ".."); };
use WebminCore;
&init_config();
