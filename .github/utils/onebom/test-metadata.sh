#!/usr/bin/bash

mkdir -p /tmp/onebom/first/0 /tmp/onebom/first/1 /tmp/onebom/first/2 /tmp/onebom/first/3 /tmp/onebom/first/4 /tmp/onebom/first/5
mkdir -p /tmp/onebom/second/0 /tmp/onebom/second/1 /tmp/onebom/second/2 /tmp/onebom/second/3 /tmp/onebom/second/4 /tmp/onebom/second/5

for i in `ls /tmp/onebom/first`
do
	echo "$i:file-$i" > /tmp/onebom/first/$i/map.txt
	echo "data" > /tmp/onebom/first/$i/requirements.txt
done

for i in `ls /tmp/onebom/second`
do
	echo "$i:file-$i" > /tmp/onebom/second/$i/map.txt
	echo "data" > /tmp/onebom/second/$i/requirements.txt
done

rm -rf /tmp/onebom/second/0

echo "data2" >> /tmp/onebom/second/2/requirements.txt

