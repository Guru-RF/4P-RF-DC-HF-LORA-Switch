import time
import board
import busio
import digitalio
import adafruit_rfm9x
import EasyCrypt
import config

print("Intializing µPico")

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

rf1 = digitalio.DigitalInOut(board.GP5)
rf1.direction = digitalio.Direction.OUTPUT

rf1.value = True
time.sleep(0.25)
rf1.value = False

rf2 = digitalio.DigitalInOut(board.GP6)
rf2.direction = digitalio.Direction.OUTPUT

rf2.value = True
time.sleep(0.25)
rf2.value = False

rf3 = digitalio.DigitalInOut(board.GP7)
rf3.direction = digitalio.Direction.OUTPUT

rf3.value = True
time.sleep(0.25)
rf3.value = False

rf4 = digitalio.DigitalInOut(board.GP8)
rf4.direction = digitalio.Direction.OUTPUT

rf4.value = True
time.sleep(0.25)
rf4.value = False

# Lora Stuff
RADIO_FREQ_MHZ = 868.775
CS = DigitalInOut(board.GP21)
RESET = DigitalInOut(board.GP20)
spi = busio.SPI(board.GP18, MOSI=board.GP19, MISO=board.GP16)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ, baudrate=1000000, agc=False,crc=True)
rfm9x.tx_power = 5

# Wait to receive packets.
print("Waiting for packets...")
# We need to retreive count from file when starting if > ?? we do a rollover
while True:
    packet = rfm9x.receive(timeout=0.5)
    if packet is not None:
        decrypted = EasyCrypt.decrypt_string(config.DEVICE, packet, config.KEY)
        if decrypted is not False:
            print("Received (decrypted): {0}".format(decrypted))
            split = decrypted.split(',', 4)

            counter = int(split[0])
            type = str(split[1])
            port = int(split[2])
            state = str2bool(split[3])

            if counter > remotecount:
                try: 
                    file = open("remotecounter", "w")
                    file.write(str(counter))
                    file.close()
                except OSError:
                    print("Cannot write remotecounter, read-only fs")
                remotecount = counter

                if port is 1:
                    rf1.value = state
                    rf2.value = False
                    rf3.value = False
                    rf4.value = False
                
                if port is 2:
                    rf1.value = False
                    rf2.value = state
                    rf3.value = False
                    rf4.value = False
                
                if port is 3:
                    rf1.value = False
                    rf2.value = False
                    rf3.value = state
                    rf4.value = False
                
                if port is 4:
                    rf1.value = False
                    rf2.value = False
                    rf3.value = False
                    rf4.value = state

                value = str(count) + ',SW,' + str(port) + ',' + str(state)
                encrypted = EasyCrypt.encrypt_string(config.DEVICE, value, config.KEY)

                time_now = time.monotonic()
                rfm9x.send(encrypted)
                print("Send (encrypted): {0}".format(value))
                sleeptime = max(0, 0.45 - (time.monotonic() - time_now))
                time.sleep(sleeptime)
                count=count+1
                if count > 1000000:
                    count = 0
                try: 
                    file = open("localcounter", "w")
                    file.write(str(count))
                    file.close()
                except OSError:
                    print("Cannot write localcounter, read-only fs")
            else:
                print("Remote counter is to low ! attack ?!")
        else:
            print("Unknown packet")