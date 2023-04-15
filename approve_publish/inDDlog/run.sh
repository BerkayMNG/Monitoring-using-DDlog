rm appub.dat
touch appub.dat

rm results.txt
touch results.txt
max=50000
curr=5000
steps=5000
batch=10

for((curr=$curr; curr <=$max; curr+=$steps))
do
    rm appub.dat
    touch appub.dat
    for((j=1; j <=$curr; j+=$batch))
    do
    echo "start;" >> appub.dat
        for ((i=$j; i <$((j+batch)); i++))
        do  
            echo "insert Timestamp($i,$i);" >> appub.dat
            echo "insert Approve($i,$i);" >> appub.dat
            echo "insert Publish($i,$i);" >> appub.dat
        done
    echo "commit dump_changes;" >> appub.dat
    done
    echo "$curr" >> results.txt
    /usr/bin/time -f'%e %M' --append --output=results.txt ./appub_ddlog/target/release/appub_cli < appub.dat > /dev/null
done


/bin/python3 eval.py