die() { printf %s "${@+$@$'\n'}" ; exit 1; }

if [ $# -ne 1 ]
then
    echo "1 argument needed"
    echo "Usage: $0 <swap file size as dd sector count>"
    echo
    echo "Example: $0 8192k"
    echo "  will make 8 GiB of swap in /swapfile"
    exit 1
fi

dd_count=$1
sudo dd if=/dev/zero of=/swapfile bs=1024 count="$dd_count" || die "Invalid dd sector count? Try <number of kilobytes>k e.g. 8192k == 8GB"

sudo mkswap /swapfile || die "Could not bake swap filesystem onto swap file"
sudo swapon /swapfile || die "Could not turn on swap file"

echo "!!! Append this to /etc/fstab if not already there:"
echo "    /swapfile       none    swap    sw      0       0"
echo
echo "Setting kernel swappiness"
echo 0 | sudo tee /proc/sys/vm/swappiness || die "Could not set kernel swappiness"
echo
echo "!!! Append this to /etc/sysctl.conf if not already there:"
echo "vm.swappiness = 0"

echo "Done"
sudo swapon -s || die "Could not list active swap"
