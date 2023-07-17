# udp_client
## 1. Envrionment
  - OS: Ubuntu 18.04
  - Language: Python 3.7
  - VirtualEnv: Anaconda3
  - IDE: PyCharm

## 2. Use

  ### 1) Make virtual environment & install dependencies :
    $ conda create -n UDP python=3.7
    $ conda activate UDP
    $ pip install opencv-python==4.6.0.66 opencv-contrib-python==4.6.0.66 numpy pyudev pyyaml ntplib pip install pynvjpeg
    $ sudo apt-get update
    $ sudo apt-get install libturbojpeg
    $ pip install -U git+https://github.com/lilohuang/PyTurboJPEG.git
    $ sudo apt install k4a-tools
    $ sudo apt install libk4a1.4
    $ sudo apt install libk4a1.4-dev
    $ pip install pyk4a

  ### 2) Download git:
    $ git clone https://github.com/UnstructuredWork/udp_client.git
  
  ### 3) Check the config file:
     > ./config/config.yaml
     ------------------------
        resolution: "1080"          # ["4K", "1080", "720"]
        fps: 60
        format: "YUYV"              # ["NV12", "YUYV"]
        subsystem: "video4linux"    
        show_fps: False             # True or False              
        
        l_serial: LEFT_CAMERA_SERIAL_NUMBER
        r_serial: RIGHT_CAMERA_SERIAL_NUMBER
     
  ### 4) Run
  ##### modify 'HOST' and 'PORT' before using
    $ python main.py
    $ python ntp.py
 
  ### 5) Synchronize time
  ##### [doc/time_synchronization.pptx](doc/time_synchronization.pptx)

  ### 6) Check time synchronization
    > python test/sync.py
    ------------------------
      NTP Server Time과 Local Time과 차이는 -1.36 ms입니다.
      NTP Server Time과 Local Time과 차이는 -1.45 ms입니다.
      NTP Server Time과 Local Time과 차이는 -1.39 ms입니다.
      NTP Server Time과 Local Time과 차이는 -1.40 ms입니다.
      NTP Server Time과 Local Time과 차이는 -1.37 ms입니다.
    
    > chronyc sources -v
    ------------------------
    210 Number of sources = 1
    
      .-- Source mode  '^' = server, '=' = peer, '#' = local clock.
     / .- Source state '*' = current synced, '+' = combined , '-' = not combined,
    | /   '?' = unreachable, 'x' = time may be in error, '~' = time too variable.
    ||                                                 .- xxxx [ yyyy ] +/- zzzz
    ||      Reachability register (octal) -.           |  xxxx = adjusted offset,
    ||      Log2(Polling interval) --.      |          |  yyyy = measured offset,
    ||                                \     |          |  zzzz = estimated error.
    ||                                 |    |           \
    MS Name/IP address         Stratum Poll Reach LastRx Last sample               
    ===============================================================================
    ^* 10.252.101.174                4  10     0   66h    +18us[  +16us] +/- 8647ms