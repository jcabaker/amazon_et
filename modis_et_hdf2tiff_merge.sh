for num in {2001..2019} ; do
        echo $num
        n=1
        max=365
        #max=9
        while [ "$n" -le "$max" ]; do
                echo $n
                if [ $n -lt 10 ]; then
                        cd "$num"/"00$n"
                else
                if [ $n -lt 100 ]; then
                        cd "$num"/"0$n"
                else
                cd "$num"/"$n"

                fi
                fi
                # Do the hdf to tiff conversion
                pwd
                if [ "$(ls -A $DIR)" ]; then
                        #echo "Take action $DIR is not Empty"
                        # change this path to the location of modis_et_merge
                        /nfs/a68/gyjcab/datasets/MODIS_ET/hdf_files_V006/data/modis_et_merge .

                else
                        echo "$DIR is Empty"
                fi
                n=`expr "$n" + 8`;
                cd ../..

done
done
