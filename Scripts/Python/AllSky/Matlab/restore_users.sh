#!/bin/bash
#Script to get all current users
#Version 1.00, Joe McCauley, School of Physics, TCD. 2022-03-02
#Found by David McKenna at https://access.redhat.com/solutions/179753

for f in {passwd,group,shadow,gshadow}.bak; do cat $f >>/etc/${f%.bak}; done

for uidgid in $(cut -d: -f3,4 passwd.bak); do
    dir=$(awk -F: /$uidgid/{print\$6} passwd.bak)
    mkdir -vm700 "$dir"; cp -r /etc/skel/.[[:alpha:]]* "$dir"
    chown -R $uidgid "$dir"; ls -ld "$dir"
done