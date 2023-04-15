rm appub.log
touch appub.log

rm results.txt
touch results.txt
max=50000
curr=1000
steps=1000
for ((curr=$curr; curr <=$max; curr+=$steps))
do
    rm appub.log
    touch appub.log
    for((i=1; i <=$curr; i++))
    do
        echo "@$((i+20)) approve($i) publish($i)" >> appub.log
    done
    echo "$curr" >> results.txt
    /usr/bin/time -f'%e %M' --append --output=results.txt monpoly -sig appub.sig -formula appub.mfotl -negate -log appub.log > /dev/null 
done

/bin/python3 eval.py