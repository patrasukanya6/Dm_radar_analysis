#!/bin/bash -l
# Process daily radar Dm data for the EarthCARE comparison workflow.
#
# The script expects two configuration files. They are sourced to provide the
# paths used by Dm_radar_comparison.py, including pathPro,
# pathOutputData, pathDmData_tempfilter, and DiffRadarPlots.
#
# For each selected date, the Python script retrieves radar Dm, applies the
# Cloudnet insect and temperature filters, writes the filtered NetCDF output,
# and saves a quicklook plot. An email notification is sent after each year.
#
# Usage:
#   ./Dm_radar_for_EarthCare_comparison.sh <config_file> <environment_file>
#
# The active date range is January-December 2025 and January-present 2026.


# Argument validation check
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <config_file>"
    exit 1
fi

source $1  # Source configuration file
source $2
#pyhton_v="$(python -V 2>&1)"
#echo $python_v


years=( '2025' '2026')
#months='04'
months1=('01' '02' '03' '04' '05' '06' '07' '08' '09' '10' '11' '12')
months2=('01' '02' '03' '04' '05' '06')
#days=('07' '08' '09')
#---month
for year in "${years[@]}"
do
if [[ "$year" == "2026" ]]
then 
	months=("${months2[@]}")
fi
if [[ "$year" == "2025" ]]
then 
	months=("${months1[@]}")
fi

if [[ "$year" == "2024" ]]
then
        months=("${months1[@]}")
fi

for month in "${months[@]}"

do
        if [[ $month == '01' ]] || [[ $month == '03' ]] || [[ $month == '05' ]] || [[ $month == '07' ]]\
                ||[[ $month == '08' ]] || [[ $month == '10' ]] || [[ $month == '12' ]]
        then
        days=('01' '02' '03' '04' '05' '06' '07' '08' '09' '10'\
                '11' '12' '13' '14' '15' '16' '17' '18' '19'\
                '20' '21' '22' '23' '24' '25' '26' '27' '28' '29' '30' '31')

        fi

                if [ $month == '02' ]
        then
        days=('01' '02' '03' '04' '05' '06' '07' '08' '09' '10'\
              '11' '12' '13' '14' '15' '16' '17' '18' '19' '20' '21' '22'\
              '23' '24' '25' '26' '27' '28' '29')

        fi


                #if [ $month == '12' ]
        #then
	#	days=('25' '26' '27' '28' '29' '30' '31') 
		#('01' '02' '03' '04' '05' '06' '07' '08' '09' '10'\
              #'11' '12')

        #fi



        if [[ $month == '04' ]]||[[ $month == '06' ]]||[[ $month == '09' ]]||[[ $month == '11' ]]
        then
        days=('01' '02' '03' '04' '05' '06' '07' '08' '09' '10'
              '11' '12' '13' '14' '15' '16' '17' '18' '19' '20' '21' '22' '23'
              '24' '25' '26' '27' '28' '29' '30')
         fi

        #---day
        for day in ${days[@]}
        do



                current_date=$year$month$day
                echo $current_date
#python $pathPro/Dm_radar_comparison_final.py $current_date $pathOutputData
#python $pathPro/Dm_Disdrometer_comparison.py $current_date $pathOutputData $pathDisdrometer
python $pathPro/Dm_radar_comparison.py $current_date $pathOutputData $pathDmData_tempfilter $DiffRadarPlots
#python $pathCalibration/radar_calibration_plots_final.py $current_date K $pathXBand  $pathKaBand $pathWBand $pathOutputMeanData $pathOffsetData $pathDisdrometer $pathOutputPlots

echo -----------------------
echo -----------------------

        done

	python $pathPro/email_notification.py

done
done
