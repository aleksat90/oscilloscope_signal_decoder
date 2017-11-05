import ripyl.sigproc as sigp
import ripyl.streaming as stream
import ripyl.protocol.i2c as i2c

def sim_i2c():
    # I2C params
    clock_freq = 100.0e3

    # Sampled waveform params
    sample_rate = clock_freq * 100.0
    rise_time = sigp.min_rise_time(sample_rate) * 10.0 # 10x min. rise time
    noise_snr = 30.0

    message = 'foobar'
    byte_msg = bytearray(message.encode('latin1')) # Get raw bytes as integers

    transfers = [i2c.I2CTransfer(i2c.I2C.Read, 0x42, byte_msg)]

    # Synthesize the waveform edge stream
    scl, sda = i2c.i2c_synth(transfers, clock_freq, idle_start=3.0e-5, idle_end=3.0e-5)

    # Convert to a sample stream with band-limited edges and noise
    cln_scl_it = sigp.synth_wave(scl, sample_rate, rise_time, tau_factor=0.7)
    cln_sda_it = sigp.synth_wave(sda, sample_rate, rise_time, tau_factor=1.5)

    # Add noise and gain
    noisy_scl_it = sigp.amplify(sigp.noisify(cln_scl_it, snr_db=noise_snr), gain=3.3, offset=0.0)
    noisy_sda_it = sigp.amplify(sigp.noisify(cln_sda_it, snr_db=noise_snr), gain=3.3, offset=0.0)

    # Capture the samples from the iterator
    noisy_scl = list(noisy_scl_it)
    noisy_sda = list(noisy_sda_it)

    return (noisy_scl, noisy_sda)


# Get scl_samples and sda_samples from external source
# noisy_scl = stream.samples_to_sample_stream(scl_samples, sample_period)
# noisy_sda = stream.samples_to_sample_stream(sda_samples, sample_period)


import matplotlib
import ripyl.util.plot as rplot
from collections import OrderedDict

noisy_scl, noisy_sda = sim_i2c() # Generate simulated sample streams

print(type(noisy_scl))
print(len(noisy_scl))

# The decoded records contain annotation information
records = list(i2c.i2c_decode(iter(noisy_scl), iter(noisy_sda)))
print('Noisy_scl:' +str(len(noisy_scl)))
print('Records:' +str(len(records)))
# for i in range(100):
#     print(records[i])
print(records)

# Define the channels ordered from top to bottom with the y-axis labels
channels = OrderedDict([('SCL (V)', noisy_scl), ('SDA (V)', noisy_sda)])
title = 'I2C plot example'
print(channels)
# The Plotter object formats the samples and annotations into plotted waveforms
plotter = rplot.Plotter()
plotter.plot(channels, records, title, label_format=stream.AnnotationFormat.Text)
plotter.show() # Show the plot in a matplotlib window
