#
# Common code for starting game servers
#

SHORTCMD=$(basename "$COMMAND")
WORKINGDIR=$(dirname "$COMMAND")
PIDFILE=${COMMAND}.pid
PORTFILE=${COMMAND}.port

. /lib/lsb/init-functions

start()
{
    start-stop-daemon --pidfile "$PIDFILE" --startas "$COMMAND" --oknodo --quiet --chuid "$USER" --chdir "$WORKINGDIR" --background --start
}

stop()
{
    start-stop-daemon --pidfile "$PIDFILE" --oknodo --quiet --stop --user "$USER"
    while [ -f "$PIDFILE" ] ; do
        sleep 1
    done
}

case "$1" in
    start)
        log_daemon_msg "Starting $DESCRIPTION server" "$SHORTCMD"
        start
        log_end_msg 0
        ;;

    stop)
        log_daemon_msg "Stopping $DESCRIPTION server" "$SHORTCMD"
        stop
        log_end_msg 0
        ;;

    force-reload|restart)
        log_daemon_msg "Restarting $DESCRIPTION server" "$SHORTCMD"
        stop
        start
        log_end_msg 0
        ;;

    status)
        start-stop-daemon --pidfile "$PIDFILE" --test --quiet --stop --user "$USER"
        if [ $? -ne 0 ] ; then
            echo "$DESCRIPTION server currently not running"
        else
            echo "$DESCRIPTION server currently running"
        fi
        ;;

    port)
        if cat $PORTFILE 2> /dev/null; then
            true
        else
            exit 1
        fi
        ;;

    *)
        echo "Usage: $0 {start|status|stop|restart|force-reload|port}"
        exit 1
        ;;
esac

exit 0
