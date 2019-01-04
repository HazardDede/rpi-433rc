# rpi-433rc

> Raspberry docker image to sniff and remote control 433mhz sockets by rest interface

## Background

TODO: Wire everything together

## Build the image

The hard work building the image will be issued by a Makefile. Make sure to run it on a raspberry machine (otherwise it will fail).

    # Clone this repository
    git clone https://github.com/HazardDede/rpi-433rc.git
    cd rpi-433rc
    # Build the image
    make -f Makefile.docker build
    
That's it. After that you should have a rpi-433rc image lying around. You can check with

    docker images | grep rpi-433rc
    
## Find out your device codes

Before using the service you have to find out the codes that your devices are listening to to make them turn on resp. off.
Fire up a container to sniff the codes:

    docker run --rm -it \
	    --name sniffy \
	    --privileged --cap-add SYS_RAWIO --device=/dev/mem \
	    hazard/rpi-433rc:latest sniff -g 27
	    
You should see that the sniffing tool has started. If your gpio pin is not 27 (default), you can pass a different one.
Push the buttons on your remote control like a madman and note the results for the different devices (on / off codes).
If you are done Ctrl + C out of it.

## Configuring your devices

Create a `device.json` file to configure your devices with the sniffed codes. Content should look similiar than this:

    {
        "device1": {
            "code_on": 12345,
            "code_off": 23456
        },
        "device2": {
            "code_on": 66567,
            "code_off": 45675
        }
    }
    
Where `device1` and `device2` are the actual names of the devices. Be creative ;-)
`code_on` and `code_off` are the actual codes you sniffed before.

## Start the rest-api

Easy one, too:
    
    # This command 
    docker run --rm \
        --name rpi-433rc \
        -p "5555:5000" \
        -e CONFIG_DIR=/conf \
        -e GPIO_OUT=17 \
        -v <path/to/your/device.json>:/conf/devices.json \
        --privileged --cap-add SYS_RAWIO --device=/dev/mem \
        hazard/rpi-433rc:latest serve
        
You can change the GPIO_OUT if you are using a different one than me.
Nicely done. Thanks to port forwarding you should see the swagger ui when navigating to the url [http://<raspi-ip>:5555](http://<raspi-ip>:5555).
Feel free to try the different endpoints.
