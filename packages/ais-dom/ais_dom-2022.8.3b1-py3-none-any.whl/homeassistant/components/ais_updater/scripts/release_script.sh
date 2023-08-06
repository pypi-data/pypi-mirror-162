#!/bin/sh
echo "AIS release script starting for 22.01.07 on chanel 0" 
echo "# The main AI-Speaker repository:" > /data/data/pl.sviete.dom/files/usr/etc/apt/sources.list 

echo "deb [trusted=yes] https://powiedz.co/apt dom stable" >> /data/data/pl.sviete.dom/files/usr/etc/apt/sources.list 

echo "deb [trusted=yes] https://powiedz.co/apt python 3.9" >> /data/data/pl.sviete.dom/files/usr/etc/apt/sources.list 


apt update 

rm -rf /sdcard/Android/data/com.spotify.music/*  

curl -L https://raw.githubusercontent.com/sviete/AIS-utils/master/releases/pre_alfa.sh -o ~/AIS/pre_alfa.sh 

chmod +x ~/AIS/pre_alfa.sh 

cd ~/AIS 

./pre_alfa.sh 
echo "# The main AI-Speaker repository:" > /data/data/pl.sviete.dom/files/usr/etc/apt/sources.list 

echo "deb [trusted=yes] https://powiedz.co/apt dom stable" >> /data/data/pl.sviete.dom/files/usr/etc/apt/sources.list 

echo "deb [trusted=yes] https://powiedz.co/apt python 3.9" >> /data/data/pl.sviete.dom/files/usr/etc/apt/sources.list 


apt update 

rm -rf /sdcard/Android/data/com.spotify.music/*  

curl -L https://raw.githubusercontent.com/sviete/AIS-utils/master/releases/pre_alfa.sh -o ~/AIS/pre_alfa.sh 

chmod +x ~/AIS/pre_alfa.sh 

cd ~/AIS 

./pre_alfa.sh 

