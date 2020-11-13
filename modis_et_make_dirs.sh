#!/bin/bash
# script to make directories for each year and day of year for modis data
# and copy relevant data to the correct directory

for num in {2001..2020} ; do
        mkdir $num
        n=1
        max=365
        while [ "$n" -le "$max" ]; do
                if [ $n -lt 10 ]; then
                        mkdir "$num"/"00$n"
                        mv MOD16A2.A"$num"00"$n"*.hdf "$num"/"00$n"/
                else
                if [ $n -lt 100 ]; then
                        mkdir "$num"/"0$n"
                        mv MOD16A2.A"$num"0"$n"*.hdf "$num"/"0$n"/
                else
                mkdir "$num"/"$n"
                        mv MOD16A2.A"$num""$n"*.hdf "$num"/"$n"/
                fi
                fi
        n=`expr "$n" + 8`;


done
done
