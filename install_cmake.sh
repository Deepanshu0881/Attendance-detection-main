# #!/bin/bash

# # Ensure that the script is running with root privileges
# if [ "$(id -u)" -ne 0 ]; then
#   echo "Please run this script with sudo or as root."
#   exit 1
# fi

# echo "Installing CMake..."

# # Update package list
# sudo apt-get update -y

# # Install dependencies
# sudo apt-get install -y software-properties-common

# # Add the CMake PPA (Personal Package Archive)
# sudo add-apt-repository -y ppa:kitware/ppa

# # Update again after adding the repository
# sudo apt-get update -y

# # Install cmake
# sudo apt-get install -y cmake

# # Check cmake version
# cmake --version

# if [ $? -eq 0 ]; then
#   echo "CMake installed successfully."
# else
#   echo "Error: CMake installation failed."
#   exit 1
# fi
