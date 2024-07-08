## File Directory

```
home/
│
└─── pi/
   │
   └─── DoorContact/
      │
      ├── config.ini
      │
      └── server.py

```

## Auto Start Service

To start the server upon boot of pi, follow steps below:

1.  Run the following commands in terminal of Raspberry Pi

```
sudo crontab -e
```

2. Within this file, add the following line to the end of the script

```
@reboot /usr/bin/python3 /home/pi/DoorContact/server.py
```

3. To test if the installation is successful, type the following into the Raspberry Pi Terminal

```
sudo reboot
```

# Authors

- [@Jasper](https://git2.logicsmartsoln.com/Jasper)
