import shutil
import pkg_resources
import yaml
import minimalmodbus
import sys
import os
import datetime
import platformdirs
import queue
from threading import Timer

global dataDirectory
global logFileName
global dataFileName
global startDateTime
global cfg
global data_q
global print_q

# Creates a repeated threading timer
class RepeatTimer(Timer):
    def run(self):
        delay = 0
        last = datetime.datetime.now().timestamp() - self.interval
        while not self.finished.wait(0.01):
            cur = datetime.datetime.now().timestamp()
            delay += cur - last
            last = cur
            if delay >= self.interval:
                delay -= self.interval
                self.function(*self.args, **self.kwargs)

# Prints a message and writes it to the log file
def printLog(directory, message):
    global logFileName

    if (message != ''):
        if cfg['print_terminal']:
            print(message)
        if cfg['print_log']:
            logFile = open(os.path.join(directory, logFileName), 'a')
            original_stdout = sys.stdout
            sys.stdout = logFile
            print(message)
            sys.stdout = original_stdout
            logFile.close()

# Adds a timestamp and list of values to the CSV file
def writeCSV(directory, timestamp, value_list):
    global dataFileName

    if cfg['csv_file']:
        dataFile = open(os.path.join(directory, dataFileName), 'a')
        headerLine = timestamp
        for value in value_list:
            headerLine += ',' + value
            
        headerLine += '\n'
        dataFile.write(headerLine)
        dataFile.close()

# Creates an empty list with a value placed at a specific index for storing to the CSV file
def createList(val_idx, total_val, formatted_val):
    value_list = []
    for idx in range(total_val):
        if idx == val_idx:
            value_list.append(str(formatted_val))
        else:
            value_list.append('')
    return value_list

# Class for reading registers
class RegisterReader():
    interval_count = 0
    def __init__(self, instrument, slaves, total_val):
        self.instrument = instrument
        self.slaves = slaves
        self.total_val = total_val

    def read_register(self):
        global dataDirectory
        global data_q
        global print_q

        self.interval_count += 1

        for slave in self.slaves:
            try:
                val_idx = 0
                self.instrument.address = slave['address']
                for register in slave['registers']:
                    # Only read from the register if the current 'interval_count' is a multiple of 'intervals'
                    if (self.interval_count % register['intervals']) == register['offset']:
                        try:
                            self.instrument.serial.timeout = float(register['timeout']) / 1000
                            reg_val = self.instrument.read_register(register['address'])
                            data_q.put([self.instrument, slave['address'], register['values'], reg_val, datetime.datetime.now(), val_idx, self.total_val])

                        except IOError as e:
                            deviceDirectory = os.path.join(dataDirectory, self.instrument.serial.port.replace('\\', '-').replace('/', '-') + '_' + '{0:#0{1}x}'.format(slave['address'], 4))
                            print_q.put([deviceDirectory, 'Error: Failed to read ' + self.instrument.serial.port + ' ' + '{0:#0{1}x}'.format(slave['address'], 4) + ' ' + '{0:#0{1}x}'.format(register['address'], 6) + ' - ' + str(e)])
                    val_idx += len(register['values'])

            except Exception as e:
                deviceDirectory = os.path.join(dataDirectory, self.instrument.serial.port.replace('\\', '-').replace('/', '-') + '_' + '{0:#0{1}x}'.format(slave['address'], 4))
                print_q.put([deviceDirectory, 'Error: Unknown exception in read_registers() - ' + str(e)])

# Handles register values in the data queue (logs them, prints them, writes them to a CSV file, etc...)
def data_handler():
    global data_q
    global print_q
    global startDateTime

    try:
        msg = data_q.get(False)

        slave_str = '{0:#0{1}x}'.format(msg[1], 4)
        deviceDirectory = os.path.join(dataDirectory, msg[0].serial.port.replace('\\', '-').replace('/', '-') + '_' + slave_str)
        try:
            for value in msg[2]:
                # If the mask is 0, skip it
                if value['mask'] == 0:
                    print_q.put([deviceDirectory, 'Error: Register mask was 0 for prefix \"' + value['prefix'] + '\"'])
                    continue

                # AND the register value with the register mask
                temp_val = msg[3] & value['mask']
                # Shift the register value and its mask until the mask has its first bit set to 1
                temp = value['mask']
                while not (temp & 0x1):
                    temp_val >>= 1
                    temp >>= 1

                # Format the value
                val = float(temp_val) / (10 ** value['decimals'])
                formatted_val = format(val, '.' + str(value['decimals']) + 'f')

                # Create the timestamp
                timestamp = msg[4].timestamp() - startDateTime.timestamp()
                float_timestamp = format(timestamp, '.3f')

                # Print the value with or without a timestamp
                if cfg['print_timestamp']:
                    str_timestamp = msg[4].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    print_q.put([deviceDirectory, '[' + str_timestamp + '] ' + msg[0].serial.port + ' ' + slave_str + ' ' + value['prefix'] + ': ' + formatted_val])
                else:
                    print_q.put([deviceDirectory, msg[0].serial.port + ' ' + slave_str + ' ' + value['prefix'] + ': ' + formatted_val])

                # Write the value to the CSV file
                writeCSV(deviceDirectory, float_timestamp, createList(msg[5], msg[6], formatted_val))
        except Exception as e:
            print_q.put([deviceDirectory, 'Error: Unknown exception in format_data() - ' + str(e)])

    except queue.Empty:
        pass

    except Exception as e:
        print('Error: Unknown exception in format_data() - ' + str(e))

# Prints out the strings in the print queue
def print_handler():
    global print_q

    try:
        msg = print_q.get(False)
        printLog(msg[0], msg[1])
    except queue.Empty:
        pass

    except Exception as e:
        printLog(msg[0], 'Error: Unknown exception in print_handler() - ' + str(e))

def main():
    global dataDirectory
    global logFileName
    global dataFileName
    global startDateTime
    global cfg
    global data_q
    global print_q

    # Create start time
    startDateTime = datetime.datetime.now()

    # Create the user data folder
    userDirectory = os.path.join(platformdirs.user_data_dir(), 'ModbusQuery')
    if not os.path.exists(userDirectory):
        os.mkdir(userDirectory)
    
    # Check the existing config
    defaultConfig = os.path.join(os.path.abspath( os.path.dirname(__file__)),'config.yaml')
    if os.path.exists(os.path.join(userDirectory, 'config.yaml')):
        with open(os.path.join(userDirectory, 'config.yaml'), 'r') as file:
            cfg = yaml.safe_load(file)
            if 'version' in cfg:
                try:
                    version = pkg_resources.get_distribution('modbus-query').version
                    if version != cfg['version']:
                        file.close()
                        os.remove(os.path.join(userDirectory, 'config.yaml'))
                except:
                    pass
            else:
                file.close()
                os.remove(os.path.join(userDirectory, 'config.yaml'))

    # Copy over the default config and use it
    if not os.path.exists(os.path.join(userDirectory, 'config.yaml')):
        shutil.copyfile(defaultConfig, os.path.join(userDirectory, 'config.yaml'))
        # Load the configuration
        with open(os.path.join(userDirectory, 'config.yaml'), 'r') as file:
            cfg = yaml.safe_load(file)

    # Create the app's data directory in the user data folder if it doesn't already exist
    dataDirectory = os.path.join(userDirectory, 'Data')
    if not os.path.exists(dataDirectory):
        os.mkdir(dataDirectory)

    # Create file names
    timestamp = startDateTime.strftime('%Y%m%d-%H%M%S')
    logFileName = 'modbus_query' + '_' + timestamp + '.log'
    dataFileName = 'modbus_query' + '_' + timestamp + '.csv'

    # Create the queues
    data_q = queue.Queue()
    print_q = queue.Queue()

    # Create the data handler threads
    for idx in range(cfg['handler_threads']):
        timer = RepeatTimer(float(cfg['handler_interval']) / 1000, data_handler)
        timer.daemon = True
        timer.start()

    # Open the serial ports, create the data files, and start the timers
    ports_open = 0
    for query in cfg['queries']:
        try:
            instrument = minimalmodbus.Instrument(query['serial_port'], 0x1F)
            instrument.serial.baudrate = query['serial_baud']
        except Exception as e:
            print('Error: Failed to open serial port ' + query['serial_port'] + ' - ' + str(e))
            continue

        ports_open += 1
        for slave in query['slaves']:
            deviceDirectory = os.path.join(dataDirectory, query['serial_port'].replace('\\', '-').replace('/', '-') + '_' + '{0:#0{1}x}'.format(slave['address'], 4))
            if not os.path.exists(deviceDirectory):
                os.mkdir(deviceDirectory)

            total_val = 0
            csv = []
            for register in slave['registers']:
                for value in register['values']:
                    csv.append(value['prefix'])
                    total_val += 1

            writeCSV(deviceDirectory, 'Time (s)', csv)
            printLog(deviceDirectory, 'Created data files in device directory: ' + deviceDirectory)

        reader = RegisterReader(instrument, query['slaves'], total_val)
        timer = RepeatTimer(float(query['interval']) / 1000, reader.read_register)
        timer.daemon = True
        timer.start()

    if ports_open == 0:
        return

    # Loop forever while timers are running
    while 1:
        # Printing is done here due to a timing issue if multiple threads are printing at the same time
        print_handler()

    print('Error, exited infinite loop...')

if __name__ == '__main__':
    main()
