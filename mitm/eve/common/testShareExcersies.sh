#!/bin/bash

os_on_ns_file="Ubuntu-EDU"
os_to_test="Ubuntu-EDU"

#Comment out any exercise that you don't want to test
declare -a exercises=(#"/share/education/WormModeling_Lehigh/;paws.ns;check.sh"
		#"/share/education/TCPSYNFlood_USC_ISI/;synflood.ns;check.sh"
		#"/share/education/OSHardening_GMU/;oshardening.ns;check.sh"
		#"/share/education/MITMARPPoisoning_USC/;arpspoof.ns;check.sh"
		#"/share/education/MITM_UCLA/;mitm.ns;check.sh"
		#+++"/share/education/Internetworking/;internetworking.ns;check.sh"
		#+"/share/education/DNS_MITM_ColoState/;mitm.ns;check.sh"
		#"/share/education/ComputerForensics_UCLA/;forensics.ns;check.sh"
		#+"/share/education/ComparingUNIXenvironments/;comparative-UNIX.ns;check.sh"
		#+++"/share/education/BGPHijack_ColoState/;bgphijack.ns;check.sh"
		#"/share/education/PermissionsFirewalls_UCLA/;permissions.ns;check.sh"
		#"/share/education/Passwords_USC_ISI/;pass.ns;check.sh"
		#"/users/dbosch/newnsandinstall/;exploits.ns;checksoftwareexploits.sh"
		#"/users/dbosch/newnsandinstall/;intro.ns;checkintro.sh"
		#"/users/dbosch/newnsandinstall/;sqlinject.ns;checksqlinjection.sh"
		#"/users/dbosch/newnsandinstall/;pathname.ns;checkpathname.sh"
		#"/users/dbosch/newnsandinstall/;buffer.ns;checkbuffer.sh"
		#+"/share/education/SecuringLegacySystems_JHU/;SecuringSystems.ns;check.sh"
		"/share/education/PermissionsFirewalls_UCLA/;permissions.ns;check.sh"
                "/share/education/ComputerForensics_UCLA/;forensics.ns;check.sh"
                )

for exercise in "${exercises[@]}"
do
	IFS=";" read -r -a arr <<< "${exercise}"
	echo "${arr[0]}"
	echo "${arr[1]}"
	echo "${arr[2]}"

	echo "--------------------------------------------------------------------" >> testExercises.log
	awk '{gsub(/$os_on_ns_file/,"$os_to_test")}1' ${arr[0]}${arr[1]} > /tmp/newnsfile.ns
	/usr/testbed/bin/modexp -w -e Modeling,share-edu-test /tmp/newnsfile.ns

	/usr/testbed/bin/swapexp -w -e Modeling,share-edu-test in
	sleep 500
	bash ${arr[0]}${arr[2]} share-edu-test modeling.isi.deterlab.net >> testExercises.log
	/usr/testbed/bin/swapexp -w -e Modeling,share-edu-test out
done

