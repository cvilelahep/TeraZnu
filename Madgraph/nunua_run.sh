#!/bin/bash

com=$1
ebeam=$(echo "$com / 2" | bc -l)
echo Beam energy is $ebeam GeV
echo COM energy is $com GeV

flav=$2
echo Generating flavor $2
# Define the process you want to simulate
#PROCESS="generate e+ e- > v$flav v$flav~ a"
PROCESS="generate e+ e- > v$flav v$flav~"

# Define the output directory
OUTPUT_DIR="ee_z_vv_isrpdf_${flav}_$com"

echo Directory is $OUTPUT_DIR

./bin/mg5_aMC << EOF
import model sm
$PROCESS
output $OUTPUT_DIR
y
launch
0
set ebeam1 $ebeam
set ebeam2 $ebeam
set lpp1 -3
set lpp2 3
set pdlabel1 isronlyll
set pdlabel2 isronlyll
done
EOF
