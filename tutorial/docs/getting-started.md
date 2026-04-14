# Getting Started

## Prerequisites

- OpenCOR >0.8.1 installed locally or available on your HPC.
- Git installed to clone the repository.
- MPI installed if you plan to run parameter identification or sensitivity analysis in parallel (see notes below).

## Initialising and Startup

**1. Install OpenCOR**

Download and install OpenCOR version 0.8.1 from this [link](https://opencor.ws/downloads/index.html). I recommend installing with zip/tarball in a directory where you have access and edit rights, such as ~/Desktop.

!!! note
    If you are not familiar with OpenCOR, you should go through the OpenCOR Tutorial before starting this

    Download the OpenCOR tutorial, which is a comprehensive tutorial including many examples: [OpenCOR Tutorial](https://tutorial-on-cellml-opencor-and-pmr.readthedocs.io/en/latest/_downloads/d271cfcef7e288704c61320e64d77e2d/OpenCOR-Tutorial-v17.pdf).

**2. Clone the project**

Clone the Circulatory Autogen project from the [GitHub repository](https://github.com/FinbarArgus/circulatory_autogen).

!!! note
    If you have not worked with git and GitHub, firstly download and install git, and then open the terminal and navigate (with terminal in Linux/Mac or gitbash in Windows) to a directory where you want the repository to be. Then write these commands to clone the project on your pc:

    - `git clone https://github.com/FinbarArgus/circulatory_autogen`

    If you want to develop the code, then create a fork of the above repo in GitHub, then do the following lines instead of the above:

    - `git clone https://github.com/<YourUsername>/circulatory_autogen`

    - `git remote add upstream https://github.com/FinbarArgus/circulatory_autogen`



## Directory Definition

In this tutorial, we define the **project_dir** as the directory where the Github Circulatory Autogen project has been cloned. For example, on our computer, this directory is as below:

`[project_dir]: ~/Documents/git_projects/Circulatory_autogen`

Also, the OpenCOR directory is needed for installing the necessary python libraries, which we defined as the **OpenCOR_dir**, e.g.:

`[OpenCOR_dir]: ~/Desktop/OpenCOR-0-8-1-Linux/`

<!-- If you have Windows but would prefer to use a linux distribution for running CA, you could install a virtual Linux machine. One of these virtual linux machines is VirtualBox Oracle, which can be downloaded from [here](https://www.virtualbox.org/). -->
 <!-- To set up the VirtualBox you would need to download the latest version of Ubuntu using this [link](https://ubuntu.com/download/desktop). -->

!!! info
    If running on the ABI HPC, you can use the installed OpenCOR version at the path: **/hpc/farg967/OpenCOR-0-8-1-Linux/** and Ignore the below installation steps, as the libraries are already installed. See [running on hpc](running-on-hpc.md)

## Python and Libraries Installation

To run OpenCOR-based workflows, you must use the Python version shipped with OpenCOR.

To install required Python packages, navigate to `[OpenCOR_dir]` and run:

!!! Note
    === "Linux"
        ```
        ./pip install <packagename>
        ```
    === "Mac"
        ```
        ./pythonshell -m pip install <packagename>
        
        ```
    === "Windows"
        ```
        ./pythonshell.bat -m pip install <packagename>
        
        ```

!!! note
    The repository includes a consolidated dependency list in `requirements.txt`. Use the OS-specific command above and replace `<packagename>` with:
    
    ```
    -r /path/to/circulatory_autogen/requirements.txt
    ```
    
    If you prefer manual installs, the key packages include:
    
    - Autogeneration: `pandas`, `pyyaml`, `rdflib` `libcellml`. 
    - Parameter identification: `mpi4py`, `sympy`, `emcee`, `corner`, `schwimmbad`, `tqdm`, `statsmodels`.
    - Sensitivity analysis: `SALib`, `seaborn`.
    - CMA-ES optimisation: `nevergrad`.
    - Utilities/tests: `ruamel.yaml`, `pytest`.

## Setting up your python path

Open `[project_dir]/user_run_files/opencor_pythonshell_path.sh` file and change the `opencor_pythonshell_path` to the directory of pythonshell in the **OpenCOR_dir**: 

!!! Note
    === "Linux and Mac"
        ```
        opencor_pythonshell_path=`<OpenCOR_dir>/pythonshell`.
        ```

    === "Windows"
        ```
        opencor_pythonshell_path=`C:\<OpenCOR_dir>\pythonshell.bat`.
        
        Note that the windows path conventions need to be used with C: and "\ rather than "/".
        ```

!!! Note
    This tutorial assumes you will be running `.sh` commands (if you're on Windows, use Git Bash). 

    Alternatively (**especially for debugging**), you can run the Python scripts directly. Use the OpenCOR Python interpreter (set in `opencor_pythonshell_path.sh`) and execute the matching script in `project_dir/src/scripts/`. The `.sh` files in `user_run_files` show the exact script each command runs.

    Option! For a more python-centric tutorial, see /tutorial/interactive/generate_and_calibrate.ipynb tutorial which shows how to run everything from python without setting up input files.

!!! warning
    Installing **mpi4py** requires mpi to be available. Therefore, the following lines may be required to install the mpi software on your computer.

    === "Linux"
        ```
        sudo apt install libopenmpi-dev
        sudo apt install libffi7
        ```
:w

    === "Mac"
        ```
        brew install openmpi
        ```
    === "Windows"

        '''
        To be able to import mpi4py, you may have to do the following:

        Download MS MPI, install both .mis and SDK.

        Set up environmental variables. Open `Control Panel` and select `Advanced System Settings`. Then select `Environmental Variables` and add the following.

            C:\Program Files\Microsoft MPI\
            C:\Program Files (x86)\Microsoft SDKs\MPI\
        '''

!!! warning 
    In versions of **OpenCOR < 0.8** you needed to nagivate to the `[OpenCOR_dir]/python/bin` directory and run the below command instead.

    ```
    ./python -m pip install <packagename>
    ```

!!! warning
    For **OpenCOR < 0.8**
    if you get an SSL error you must do the following before the pip install:

        cd [OpenCOR_dir]/python/bin
        export LD_LIBRARY_PATH=[OpenCOR_dir]/lib

    This would let the system know where to look for libcrypto.so.3 when loading the ssl module.


## Expected outcome

You should now have:

- A working OpenCOR Python environment with project dependencies installed.
- A clone of the repository ready for running the tutorial scripts.
- `opencor_pythonshell_path.sh` configured to your OpenCOR installation.
