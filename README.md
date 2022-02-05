# Wi-Fi probe counter

Inspiration: https://github.com/schollz/howmanypeoplearearound

## Setup

What you will need:

- A Raspberry Pi 4
- A AR9271 based 802.11n dongle

Steps:

At first, you need to flash a 64-bit ARM Ubuntu server image to a SD card.
I prefer Ubuntu above Raspian as I tend to experience way less driver issues on Ubuntu.

Plugin the Wi-Fi dongle and verify that it is correctly detected:

```bash
ubuntu@pi~$ lsusb
Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 003: ID 0cf3:9271 Qualcomm Atheros Communications AR9271 802.11n # <-- This line is important
Bus 001 Device 002: ID 2109:3431 VIA Labs, Inc. Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
```

Run `iw dev` to view a list of available wireless interfaces:

```bash
phy#1
	Interface wlx8416f915a678
		ifindex 4
		wdev 0x100000001
		addr 84:16:f9:15:a6:78
		type managed
		txpower 0.00 dBm
phy#0
	Interface wlan0
		ifindex 3
		wdev 0x1
		addr e4:5f:01:27:e1:75
		type managed
		channel 34 (5170 MHz), width: 20 MHz, center1: 5170 MHz
```

If you are not sure, which interface is the right one, run `iw phy`:

```bash
Wiphy phy1
	wiphy index: 1
	max # scan SSIDs: 4
	max scan IEs length: 2257 bytes
	max # sched scan SSIDs: 0
	max # match sets: 0
	Retry short limit: 7
	Retry long limit: 4
	Coverage class: 0 (up to 0m)
	Device supports RSN-IBSS.
	Device supports T-DLS.
	Supported Ciphers:
		* WEP40 (00-0f-ac:1)
		* WEP104 (00-0f-ac:5)
		* TKIP (00-0f-ac:2)
		* CCMP-128 (00-0f-ac:4)
		* CCMP-256 (00-0f-ac:10)
		* GCMP-128 (00-0f-ac:8)
		* GCMP-256 (00-0f-ac:9)
		* CMAC (00-0f-ac:6)
		* CMAC-256 (00-0f-ac:13)
		* GMAC-128 (00-0f-ac:11)
		* GMAC-256 (00-0f-ac:12)
	Available Antennas: TX 0x1 RX 0x1
	Configured Antennas: TX 0x1 RX 0x1
	Supported interface modes:
		 * IBSS
		 * managed
		 * AP
		 * AP/VLAN
		 * monitor                # <-- Search for the device that is capable of running in monitor mode
		 * mesh point
		 * P2P-client
		 * P2P-GO
		 * outside context of a BSS
```

From the example above we can see, that `phy1` is capable of running in monitor mode and that there is an interface `wlx8416f915a678` for it.

Enable monitor mode:

```bash
sudo ifconfig wlx8416f915a678 down
sudo iwconfig wlx8416f915a678 mode monitor
sudo ifconfig wlx8416f915a678 up
```

and verify that it is actually in monitor mode:

```bash
ubuntu@docker-pi:~$ iw dev
phy#1
	Interface wlx8416f915a678
		ifindex 4
		wdev 0x100000001
		addr 84:16:f9:15:a6:78
		type monitor    # <-- It worked! :-)
		channel 1 (2412 MHz), width: 20 MHz (no HT), center1: 2412 MHz
		txpower 20.00 dBm
```

Install tshark:

`sudo apt-get install tshark`

Make it run as a non-root user:
```bash
sudo dpkg-reconfigure wireshark-common     (select YES)
sudo usermod -a -G wireshark ${USER:-root}
newgrp wireshark
```

Verify that you can capture some packets:

```
$ tshark -i wlx8416f915a678
  ...
  409 0.948606670 Routerbo_c8:76:eb (48:8f:5a:c8:76:eb) (TA) → SichuanA_f8:b0:0c (d4:b7:61:f8:b0:0c) (RA) 802.11 68 802.11 Block Ack, Flags=........C
  410 0.948616133 Routerbo_c8:76:eb (48:8f:5a:c8:76:eb) (TA) → SichuanA_f8:b0:0c (d4:b7:61:f8:b0:0c) (RA) 802.11 68 802.11 Block Ack, Flags=........C
  411 0.949088720              → SichuanA_f8:b0:0c (d4:b7:61:f8:b0:0c) (RA) 802.11 50 Clear-to-send, Flags=........C
  412 0.949506549 Routerbo_c8:76:eb (48:8f:5a:c8:76:eb) (TA) → SichuanA_f8:b0:0c (d4:b7:61:f8:b0:0c) (RA) 802.11 68 802.11 Block Ack, Flags=........C
  413 0.949516068 Routerbo_c8:76:eb (48:8f:5a:c8:76:eb) (TA) → SichuanA_f8:b0:0c (d4:b7:61:f8:b0:0c) (RA) 802.11 68 802.11 Block Ack, Flags=........C
  414 0.949782732              → SichuanA_f8:b0:0c (d4:b7:61:f8:b0:0c) (RA) 802.11 50 Clear-to-send, Flags=........C
  415 0.950001174 Routerbo_c8:76:eb (48:8f:5a:c8:76:eb) (TA) → SichuanA_f8:b0:0c (d4:b7:61:f8:b0:0c) (RA) 802.11 68 802.11 Block Ack, Flags=........C
  416 0.973785853 Routerbo_c8:69:3a → Broadcast    802.11 326 Beacon frame, SN=3468, FN=0, Flags=........C, BI=100, SSID=Tyrion WLANister
  417 1.004221297 2e:87:df:b7:72:89 → Broadcast    AWDL 383 Periodic Synchronization
  418 1.008592085              → SichuanA_f8:b0:0c (d4:b7:61:f8:b0:0c) (RA) 802.11 50 Clear-to-send, Flags=........C
  419 1.008976266 Routerbo_c8:76:eb (48:8f:5a:c8:76:eb) (TA) → SichuanA_f8:b0:0c (d4:b7:61:f8:b0:0c) (RA) 802.11 68 802.11 Block Ack, Flags=........C
  420 1.008989896 Routerbo_c8:76:eb (48:8f:5a:c8:76:eb) (TA) → SichuanA_f8:b0:0c (d4:b7:61:f8:b0:0c) (RA) 802.11 68 802.11 Block Ack, Flags=........C
  421 1.009500038              → SichuanA_f8:b0:0c (d4:b7:61:f8:b0:0c) (RA) 802.11 50 Clear-to-send, Flags=........C
  422 1.009903701 Routerbo_c8:76:eb (48:8f:5a:c8:76:eb) (TA) → SichuanA_f8:b0:0c (d4:b7:61:f8:b0:0c) (RA) 802.11 68 802.11 Block Ack, Flags=........C
  423 1.009916164 Routerbo_c8:76:eb (48:8f:5a:c8:76:eb) (TA) → SichuanA_f8:b0:0c (d4:b7:61:f8:b0:0c) (RA) 802.11 68 802.11 Block Ack, Flags=........C
  424 1.010300493              → SichuanA_f8:b0:0c (d4:b7:61:f8:b0:0c) (RA) 802.11 50 Clear-to-send, Flags=........C
  425 1.010522083 Routerbo_c8:76:eb (48:8f:5a:c8:76:eb) (TA) → SichuanA_f8:b0:0c (d4:b7:61:f8:b0:0c) (RA) 802.11 68 802.11 Block Ack, Flags=........C
  426 1.010995838              → ChinaDra_d7:f4:ba (3c:7a:aa:d7:f4:ba) (RA) 802.11 50 Acknowledgement, Flags=........C
  427 1.012493137              → ChinaDra_d7:f4:ba (3c:7a:aa:d7:f4:ba) (RA) 802.11 50 Acknowledgement, Flags=........C
  428 1.024018240 Routerbo_c8:76:eb → Broadcast    802.11 326 Beacon frame, SN=2908, FN=0, Flags=........C, BI=100, SSID=Tyrion WLANister
  ...
```

Your output should look something like the lines shown above.