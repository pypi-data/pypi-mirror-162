#!/bin/bash
#Requirement: unzip, libncurses5

installationdir="TOREPLACE_INSTALLATION_DIR"
matlabver="TOREPLACE_MATLAB_VER"
runtimever="TOREPLACE_RUNTIME_VER"
functiondir="TOREPLACE_FUNCTION_DIR"
functionname="TOREPLACE_FUNCTION_NAME"
functionargs="TOREPLACE_FUNCTION_ARGS"

libmwmclmcrrt=v${runtimever::${#runtimever}-2}${runtimever:(-1)}
MCRver=MCR_${matlabver}_glnxa64

chmod u+x ${functiondir}/files/bin/run_${functionname}.sh
chmod u+x ${functiondir}/files/bin/${functionname}
${functiondir}/files/bin/./run_${functionname}.sh ${installationdir}/$MCRver/$libmwmclmcrrt $functionargs

