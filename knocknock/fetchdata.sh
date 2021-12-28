#!/bin/bash

for url in $(lynx -dump https://www.41051.com/xmaslyrics/|grep xmasl|grep html|awk '{print $2}'); 
do 
    echo $url
    fn=$(echo $url | sed 's:.*/::'); 
    lynx -dump $url > $fn ;
done

