import broadlink
import sqlite3
import time


if __name__ == "__main__":


    while True:

        room = input("Let's begin\nWhat is the room where the device is?\n")
        device = input("Nice, What is the device's name?\n")
        function = input("Cool, What is the function we are learning?\n")

        file_name = "/angel/broadlink/codes/" + room + "_" + device + "_" + function + ".txt"

        print("Perfect, file name is going to be:",file_name)

        devices = broadlink.discover(timeout=5)
        print (devices[0].auth())
        devices[0].enter_learning()
        time.sleep(10)


        ir_packet = devices[0].check_data()

        print("Learnt data:",ir_packet)
        #devices[0].send_data(ir_packet)


        # Pass "wb" to write a new file, or "ab" to append
        with open(file_name, "wb") as binary_file:
            # Write text or bytes to the file
            num_bytes_written = binary_file.write(ir_packet)
            print("Wrote %d bytes." % num_bytes_written)

        print("Saved!\nNow we are going to test it...")
        time.sleep(5)



        in_file = open(file_name, "rb") # opening for [r]eading as [b]inary
        data = in_file.read() # if you only wanted to read 512 bytes, do .read(512)
        in_file.close()


        print('Readed:', data,"Take a look of your device to check function works well")

        for x in range(0, 10):
            devices[0].send_data(data)
            time.sleep(1)

        print('Perhaps, it works well. Enjoy your device!\n')

        bool = input("Do you want to learn another code? (y/n)\n")
        if (bool == "n"):
            break
