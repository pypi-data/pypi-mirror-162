#!/data/data/com.termux/files/usr/bin/sh
echo "--------------------------------" >> /data/data/com.termux/files/home/AIS/www/upgrade_log.txt
echo "UPDATE AIS dom, linux and python" >> /data/data/com.termux/files/home/AIS/www/upgrade_log.txt
echo $(date '+%Y %b %d %H:%M') start >> /data/data/com.termux/files/home/AIS/www/upgrade_log.txt
echo "Step 1 update the AIS dom Linux box" >> /data/data/com.termux/files/home/AIS/www/upgrade_log.txt
apt update >> /data/data/com.termux/files/home/AIS/www/upgrade_log.txt
apt upgrade -y >> /data/data/com.termux/files/home/AIS/www/upgrade_log.txt

echo "Step 2 update the AIS dom python app" >> /data/data/com.termux/files/home/AIS/www/upgrade_log.txt
pip install ais_dom -U >> /data/data/com.termux/files/home/AIS/www/upgrade_log.txt

echo "Step 3 update the android app and restart" >> /data/data/com.termux/files/home/AIS/www/upgrade_log.txt
am start -n launcher.sviete.pl.domlauncherapp/.LauncherActivity -e command ais-dom-update >> /data/data/com.termux/files/home/AIS/www/upgrade_log.txt

echo "Step 4 pm2 restart ais" >> /data/data/com.termux/files/home/AIS/www/upgrade_log.txt
pm2 restart ais >> /data/data/com.termux/files/home/AIS/www/upgrade_log.txt

echo $(date '+%Y %b %d %H:%M') end >> /data/data/com.termux/files/home/AIS/www/upgrade_log.txt
echo " " >> /data/data/com.termux/files/home/AIS/www/upgrade_log.txt
