#!/bin/bash
#Requirement: unzip, libncurses5

installationdir="TOREPLACE_INSTALLATION_DIR"
matlabver="TOREPLACE_MATLAB_VER"
runtimever="TOREPLACE_RUNTIME_VER"

libmwmclmcrrt=v${runtimever::${#runtimever}-2}${runtimever:(-1)}
MCRver=MCR_${matlabver}_glnxa64

mkdir -p ${installationdir}
mkdir -p ${installationdir}/${MCRver}_install ${installationdir}/${MCRver}
wget -O ${installationdir}/${MCRver}_installer.zip https://ssd.mathworks.com/supportfiles/downloads/${matlabver}/deployment_files/${matlabver}/installers/glnxa64/${MCRver}_installer.zip
unzip -d ${installationdir}/${MCRver}_install ${installationdir}/${MCRver}_installer.zip

${installationdir}/${MCRver}_install/./install -mode silent -agreeToLicense yes -destinationFolder ${installationdir}/${MCRver}
rm ${installationdir}/${MCRver}_installer.zip

