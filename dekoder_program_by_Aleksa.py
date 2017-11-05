import ripyl
#Importuj dekoder za dekodovanje
import ripyl.protocol.lin as lin
#import ripyl.protocol.uart as uart
#Impotovanje data seta
import csv


#CRTANJE GRAFIKA
import matplotlib
import ripyl.util.plot as rplot
from collections import OrderedDict
import ripyl.streaming as stream

#Za LeCroy osciloskop CSV reader. Ukoliko ne radi, izbrisati header iz csv file.
def read_lecroy_csv(fname):
    sample_period = 0.0
    raw_samples = []

    with open(fname, 'rb') as csvfile:
        c = csv.reader(csvfile)

        # Sample period is in cell B2 (1,1)
        # Time is in column D (3)
        # Samples are in column E (4)

        for row_num, row in enumerate(c):
            if row_num == 1: # get the sample period
                sample_period = float(row[0])
                break

        csvfile.seek(0)
        for row in c:
            raw_samples.append(float(row[1]))

    return raw_samples, sample_period



raw_samples, sample_period = read_lecroy_csv('dataset_oscilloscope_read.csv')
print('Raw samples: ' + str(type(raw_samples)) + "size: " + str(len(raw_samples)))

#Razlika izmedju dva uzorkovanja. Protictati iz CSV file ili sa osciloskopa
sample_period = 0.0000004
#Pretvorio sam stream u listu
txd = list(ripyl.streaming.samples_to_sample_stream(raw_samples, sample_period, start_time=0.0, chunk_size=100000))
records = list(uart.lin_decode(iter(txd), bits=8, parity='even', stop_bits=1))
#records = list(lin.lin_decode(iter(txd)))

# niz_podataka = []

# print(len(records))
# print(records[1])
# for i in range(len(records)):
#     niz_podataka.append(records[i].getData())


# Define the channels ordered from top to bottom with the y-axis labels
channels = OrderedDict([('TXD (V)', txd)])
# print(type(channels))
title = 'LIN plot'

# print(records)
# print(channels)

# The Plotter object formats the samples and annotations into plotted waveforms
plotter = rplot.Plotter()
plotter.plot(channels, records, title,label_format=stream.AnnotationFormat.Text)
#plotter.plot(channels, records,  title)
plotter.show() # Show the plot in a matplotlib window
