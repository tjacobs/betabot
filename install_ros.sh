sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
sudo apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net:80 --recv-key 421C365BD9FF1F717815A3895523BAEEB01FA116

sudo apt-get update
sudo apt-get upgrade

sudo apt-get install -y python-rosdep python-rosinstall-generator python-wstool python-rosinstall build-essential cmake

sudo rosdep init
rosdep update

mkdir -p ~/ros_catkin_ws
cd ~/ros_catkin_ws

rosinstall_generator desktop --rosdistro kinetic --deps --wet-only --tar > kinetic-desktop-wet.rosinstall
wstool init src kinetic-desktop-wet.rosinstall
# wstool update -j4 -t src

# collada_urdf will fail

mkdir -p ~/ros_catkin_ws/external_src
cd ~/ros_catkin_ws/external_src
wget http://sourceforge.net/projects/assimp/files/assimp-3.1/assimp-3.1.1_no_test_models.zip/download -O assimp-3.1.1_no_test_models.zip
unzip assimp-3.1.1_no_test_models.zip
cd assimp-3.1.1
cmake .
make
sudo make install

# Or exclude it 
# rosinstall_generator desktop --rosdistro kinetic --deps --wet-only --exclude collada_parser collada_urdf --tar > kinetic-desktop-wet.rosinstall

cd ~/ros_catkin_ws
rosdep install -y --from-paths src --ignore-src --rosdistro kinetic -r --os=debian:jessie

sudo ./src/catkin/bin/catkin_make_isolated --install -DCMAKE_BUILD_TYPE=Release --install-space /opt/ros/kinetic

source /opt/ros/kinetic/setup.bash

#echo "source /opt/ros/kinetic/setup.bash" >> ~/.bashrc