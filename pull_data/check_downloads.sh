#!/usr/bin/env bash

#this script loops through cam?-ccd? directories, and checks that
# (a) there is one fits file for each command line argument.
# (b) all the files have 17MB of data

#if there are less fits files, it looks for any that were missed and
#reruns the curl command from the download file.

#if there are more fits files than expected, it exists with error code 2.

set -euo

segment1=$(ls hlsp_tica_tess_ffi_s*-o*-cam1-ccd1_tess_v01_ffis.sh | awk -F- '{print $2}')
sectoruse=$(ls hlsp_tica_tess_ffi_s*-o*-cam1-ccd1_tess_v01_ffis.sh | awk -F- '{print $1}' | awk -F_ '{print $5}')

echo 'seg 1', $segment1
logstring=$(printf "|%5s| %7s|" $sectoruse $segment1)





for ii in 1 2 3 4; do
    for jj in 1 2 3 4; do

	echo $ii $jj

	segment=$(ls hlsp_tica_tess_ffi_"$sectoruse"-o*-cam"$ii"-ccd"$jj"_tess_v01_ffis.sh | awk -F- '{print $2}')
	echo $segment, $segment1
	[[ $segment != $segment1 ]] && { echo "mismatched orbit segments in download scripts, exiting"; exit 2;}

	[[ -d "cam$ii""-ccd$jj"/"$segment" ]] || {
	    mkdir -p "cam$ii""-ccd$jj"/"$segment" ;
	}

	
	scriptuse="hlsp_tica_tess_ffi_"$sectoruse"-"$segment"-cam"$ii"-ccd"$jj"_tess_v01_ffis.sh"
	
	#subtract 1 for the shebang
	Ncommands=$(wc -l $scriptuse | awk '{print $1-1}')
	echo "Ncommands (N files):" $Ncommands $scriptuse
	
	if [[ -d "$sectoruse""/cam$ii""-ccd$jj" ]]; then
	    Nfiles=$(ls "$sectoruse""/cam$ii""-ccd$jj"/hlsp*fits | wc -l)
	else
	    continue
	fi

	#check that they are all 17M
	#if not, delete the file and try again	
	for f in $(ls "$sectoruse""/cam$ii""-ccd$jj"/hlsp*fits); do

	    flag=0
	    while [[ $flag == 0 ]]; do
		fsize=$(ls -lrth $f | awk '{print $5}')
		[[ $fsize == "17M" ]] && {
		    flag=1
		} || {
		    echo "debug" $fsize $flag $scriptuse
		    cmd=$(grep $f $scriptuse);
		    echo $cmd
		    echo $cmd >>tmp ;
		    rm $f;
		    bash tmp;
		    rm tmp;		    		    
		}

	    done
	done
	
	if [[ $Ncommands == $Nfiles ]]; then
	    #this is the pass condition. All is well.
	    #move file up one level, 
	    #and log the download
	
	    logstringadd=$(printf " |%9s|" $Ncommands)
	    logstring="$logstring""$logstringadd"
	    mv "$sectoruse""/cam$ii""-ccd$jj"/* "cam$ii""-ccd$jj"/"$segment"/
	elif [[ $Ncommands -gt $Nfiles ]]; then

	    flag=0
	    
	    #fail condition---find the missing files
	    #and download
	    while [[ $flag == 0 ]]; do
		for f in $(awk '{print $5}' $scriptuse ); do
		    #pwd
		    #echo $f ${f:1:-1}
		    [[ -e ${f:1:-1} ]] || {
			#echo $f
			cmd=$(grep $f $scriptuse);
			echo $cmd >>tmp ;
			bash tmp;
			rm tmp;
		    }		   
		done
		Nfiles=$(ls "$sectoruse""/cam$ii""-ccd$jj"/hlsp*fits | wc -l)
		[[ $Ncommands == $Nfiles ]] && {
		    flag=1;
		    logstringadd=$(printf " |%9s|" $Ncommands)
		    logstring="$logstring""$logstringadd"
		    mv "$sectoruse""/cam$ii""-ccd$jj"/* "cam$ii""-ccd$jj"/"$segment"/
		}
		
	    done
	else
	    #fail condition---more files than expected?
	    #something went very wrong. exit the program and clean up
	    echo "More files in target directory s$sectoruse than expected."
	    echo "Check what is there and then clean up."
	    exit 2
	fi
    done
done

echo $logstring >> ../download-log.txt

#check that download is now empty
Nremainder=0
for ii in 1 2 3 4; do
    for jj in 1 2 3 4; do
	nadd=$(ls $sectoruse"/cam$ii""-ccd$jj" | wc -l)
	Nremainder=$(($Nremainder+$nadd))
    done
done

[[ $Nremainder == 0 ]] && {
    rm -fr $sectoruse;
    }

for downloadscript in $(ls hlsp_tica*sh); do
    if [[ -d download-scripts ]]; then
        mv $downloadscript download-scripts;
    else
	mkdir download-scripts
	mv $downloadscript download-scripts
    fi
done

echo "finished check_downloads.sh"
