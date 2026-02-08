#!/bin/bash 

### IMPORTANT NOTE: it's safer to specify absolute paths only, as folders with solvers and input files might change location one with respect to the other

FOLDERcoupler="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# FOLDERcpp="/hpc/bghi639/Software/1D-0D-coupler-cpp-example/CA_files/generated_models/aortic_bif_hybrid_new_cpp"
# FOLDERcpp="/hpc/bghi639/Software/1D-0D-coupler-cpp-example/CA_files/generated_models/aortic_bif_hybrid_new2_cpp"
# FOLDERcpp="/hpc/bghi639/Software/1D-0D-coupler-cpp-example/CA_files/generated_models/aortic_bif_hybrid_new2_RK4_cpp"
# FOLDERcpp="/hpc/bghi639/Software/1D-0D-coupler-cpp-example/CA_files/generated_models/aortic_bif_hybrid_new2_PETSC_cpp"
# FOLDERcpp="/hpc/bghi639/Software/1D-0D-coupler-cpp-example/CA_files/generated_models/aortic_bif_hybrid_new2_CVODE_cpp"
# FOLDERcpp="/hpc/bghi639/Software/1D-0D-coupler-cpp-example/CA_files/generated_models/aortic_bif_hybrid_new3_cpp"

# FOLDERcpp="/hpc/bghi639/Software/1D-0D-coupler-cpp-example/CA_files/generated_models/3compartment_hybrid_cpp"
# FOLDERcpp="/hpc/bghi639/Software/1D-0D-coupler-cpp-example/CA_files/generated_models/3compartment_mod_hybrid_v1_cpp"

# FOLDERcpp="/hpc/bghi639/Software/1D-0D-coupler-cpp-example/CA_files/generated_models/aortic_bif_hybrid_multi_cpp"

# FOLDERcpp="/hpc/bghi639/Software/VITAL_TrainingSchool2_Tutorials/cvs_model_hybrid/generated_models/cvs_model_hybrid_cpp"
# FOLDERcpp="/hpc/bghi639/Software/VITAL_TrainingSchool2_Tutorials/cvs_model_hybrid_OL/generated_models/cvs_model_hybrid_OL_cpp"
FOLDERcpp="/hpc/bghi639/Software/VITAL_TrainingSchool2_Tutorials/cvs_model_with_arm_hybrid/generated_models/cvs_model_with_arm_hybrid_cpp"

FILEconfig="coupler_config.json"

USE_PETSC=1
# USE_PETSC=0

# cd /hpc/bghi639/Software/1D-0D-coupler-cpp-example/CA_files/generated_models/aortic_bif_hybrid_new_cpp
cd "$FOLDERcpp" || exit 1

# echo "DEBUG 1: $FOLDERcpp"

# spack load sundials

if [[ "$USE_PETSC" -eq 1 ]]; then
    make -f MakefilePETSC clean
    make -f MakefilePETSC
else
    make -f Makefile clean
    make -f Makefile
    export LD_LIBRARY_PATH=$(spack location -i sundials)/lib:$LD_LIBRARY_PATH
fi
# make clean
# make
# export LD_LIBRARY_PATH=$(spack location -i sundials)/lib:$LD_LIBRARY_PATH

# echo "DEBUG 2"

# cd /hpc/bghi639/Software/1D-0D-coupler-cpp-example/CA_coupler_scripts
cd "$FOLDERcoupler" || exit 1

# echo "DEBUG 3: $FOLDERcoupler"

# rm -f coupler
# g++ -o coupler coupler.cpp coupler_auxFun.cpp -I/home/bghi639/spack/opt/spack/linux-skylake/nlohmann-json-3.11.3-bikxnolsvrkv2sx2ekbznmxn6kqdrmcw/include

# make clean
# make clean_pipe
# make
make -f Makefile clean
make -f Makefile clean_pipe
make -f Makefile

# echo "DEBUG 4"

# # rm -f zero_to_*
# # rm -f one_to_*
# # rm -f parent_to_*
# # rm -f /tmp/zero_to_*
# # rm -f /tmp/one_to_*
# # rm -f /tmp/parent_to_*
# rm -f /home/bghi639/Software/tmp/zero_to_*
# rm -f /home/bghi639/Software/tmp/one_to_*
# rm -f /home/bghi639/Software/tmp/parent_to_*

echo "*** RUNNING THE COUPLER NOW ***"

# ./coupler "/hpc/bghi639/Software/1D-0D-coupler-cpp-example/CA_files/generated_models/aortic_bif_hybrid_new_cpp/coupler_config.json"
# ./coupler "/hpc/bghi639/Software/1D-0D-coupler-cpp-example/CA_files/generated_models/aortic_bif_hybrid_new_cpp/coupler_config.json" > log_$(date +'%Y-%m-%d_%H-%M-%S').txt
# ./coupler "/hpc/bghi639/Software/1D-0D-coupler-cpp-example/CA_files/generated_models/aortic_bif_hybrid_new_cpp/coupler_config.json" > log_$(date +'%Y-%m-%d_%H-%M-%S').txt &
### for both stdout and stderr to go into the same timestamped log file
# ./coupler "/hpc/bghi639/Software/1D-0D-coupler-cpp-example/CA_files/generated_models/aortic_bif_hybrid_new_cpp/coupler_config.json" > log_$(date +'%Y-%m-%d_%H-%M-%S').txt 2>&1 &

./coupler "$FOLDERcpp/$FILEconfig"
# ./coupler "$FOLDERcpp/$FILEconfig" > log_$(date +'%Y-%m-%d_%H-%M-%S').txt
# ./coupler "$FOLDERcpp/$FILEconfig" > log_$(date +'%Y-%m-%d_%H-%M-%S').txt & 
# ./coupler "$FOLDERcpp/$FILEconfig" > log_$(date +'%Y-%m-%d_%H-%M-%S').txt 2>&1 &

echo "*** SUCCESS $(date +'%Y-%m-%d_%H-%M-%S') ***"
