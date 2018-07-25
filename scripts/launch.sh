nvidia-docker run -it -v /home/ubuntu/YNet_data:/YNet/datasets -v results:/YNet/YNet_dev/results -p 8889:8888 wmapernice/ynet_docker_files:$1
