#!/usr/bin/env python3

from twopilabs.sense.x1000 import SenseX1000
import logging
import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal.windows as windows
import scipy.constants as const
import signal
import argparse
import time

DEFAULT_FSTART = 182
DEFAULT_FSTOP = 126
DEFAULT_TSWEEP = 1
DEFAULT_NSWEEPS = 1
DEFAULT_TPERIOD = 20
DEFAULT_SWEEPMODE = SenseX1000.SweepMode.NORMAL.name


close = False

def plot(config: dict, data: SenseX1000.AcqData):
    ####
    # Process
    ####

    # Normalize data values to fullscale signed N-bit integer
    # At this point data.array is of dimension N_sweeps x N_trace x N_points
    sweep_data = data.array / data.header.acq_dtype.info.mag

    # Processing and plotting below expects a N_sweeps x N_points array. Thus select trace 0 only
    sweep_data = sweep_data[:, 0, :]

    # FFT processing to get range information,
    fft_length = max(8192, data.n_points)
    window_data = windows.hann(data.n_points, sym=False)[np.newaxis,:]
    space_data = np.fft.fftn(sweep_data * window_data, s=[fft_length], axes=[-1])

    # renormalize magnitude to dBFS
    space_data_abs = np.abs(space_data)/ np.sum(window_data)  # Renormalize for windowing function
    space_data_db = 20 * np.log10(space_data_abs)

    if not plt.fignum_exists(1):
        ####
        # Generate axes for plotting
        ####
        sweep_range = np.arange(0, data.n_points)
        sweep_time_axis = sweep_range * config['SWEEP']['TIME'] / config['SWEEP']['POINTS']
        sweep_freq_axis = config['FREQUENCY']['START'] + sweep_range * config['FREQUENCY']['SPAN'] / config['SWEEP']['POINTS']

        space_range = np.arange(0, fft_length//2)
        space_freq_axis = space_range * config['SWEEP']['POINTS'] / config['SWEEP']['TIME'] / fft_length
        space_dist_axis = space_range * config['SWEEP']['POINTS'] / abs(config['FREQUENCY']['SPAN']) / 2 * const.c / fft_length

        ####
        # Plot
        ####
        # First call of plot function. Create plots
        fig, (ax_sweep, ax_space) = plt.subplots(2, 1, figsize=(16, 14))
        fig.canvas.set_window_title('Sense X1000 Live Plot (Press "a" for Autoscale)')

        # Connect event handler for closing plot
        def exit(event):
            global close
            close = True

        def keypress(event):
            if event.key == 'a':
                plot.ax_sweep.relim()
                plot.ax_sweep.autoscale(enable=True, axis='y')

        fig.canvas.mpl_connect('close_event', exit)
        fig.canvas.mpl_connect('key_press_event', keypress)

        plt.ion() # Interactive mode on

        # Sweep Domain plot
        ax_sweep.set_xlabel("Sweep Time [ms]")
        ax_sweep.set_xlim(sweep_time_axis[0] * 1E3, sweep_time_axis[-1] * 1E3)
        ax_sweep.set_ylabel("Amplitude in Full-Scale")
        ax_sweep.set_title("Acquired raw IF sweep domain signal")
        ax_sweep.grid()

        # Add second X axis
        ax_sweep_freq = ax_sweep.twiny()
        ax_sweep_freq.set_xlabel("Instantaneous Sweep Frequency [GHz]")
        ax_sweep_freq.set_xlim(round(sweep_freq_axis[0] / 1E9, 1), round(sweep_freq_axis[-1] / 1E9, 1))

        # Spatial Domain plot
        ax_space.set_xlabel("Distance [m]")
        ax_space.set_xlim(space_dist_axis[0], space_dist_axis[-1])
        ax_space.set_ylabel("Magnitude [dBFS]")
        ax_space.set_ylim(-120, 0)
        ax_space.set_title("Fourier Transformed IF signal")
        ax_space.grid()

        # Add second X axis
        ax_space_freq = ax_space.twiny()
        ax_space_freq.set_xlabel("IF Frequency [MHz]")
        ax_space_freq.set_xlim(round(space_freq_axis[0] / 1E6, 1), round(space_freq_axis[-1] / 1E6, 1))

        # Draw both plots and store some variables as attributes to this function
        plot.gr_sweep = ax_sweep.plot(sweep_time_axis * 1E3, sweep_data.T)
        plot.gr_space = ax_space.plot(space_dist_axis, space_data_db[:, 0:fft_length//2].T)
        plot.fig = fig
        plot.ax_sweep = ax_sweep
        plot.ax_sweep_freq = ax_sweep_freq
        plot.ax_space = ax_space
        plot.ax_space_freq = ax_space_freq

        # Show plot
        fig.tight_layout()
        plt.show()
        plt.pause(0.001) # Seems to be required for MacOS?
    else:
        # Plot already exists, update data and redraw
        for i in range(0, len(plot.gr_sweep)):
            plot.gr_sweep[i].set_ydata(sweep_data[i, :])
        for i in range(0, len(plot.gr_space)):
            plot.gr_space[i].set_ydata(space_data_db[i, 0:fft_length//2])
        plot.fig.canvas.draw()
        plot.fig.canvas.flush_events()
        plt.pause(0.001)

def main():
    def exit(signum, frame):
        global close
        close = True

    logger = logging.getLogger(__name__)
    signal.signal(signal.SIGTERM, exit)
    signal.signal(signal.SIGINT, exit)

    argparser = argparse.ArgumentParser(description="Live plot for Sense X1000 radar devices")
    argparser.add_argument("-v",        dest="verbose",     action="count",         default=0,                  help="output verbose logging information (Can be specified multiple times)")
    argparser.add_argument("--fstart",  dest="fstart",      metavar="GIGAHERTZ",    default=DEFAULT_FSTART,     type=float, help="Sweep start frequency")
    argparser.add_argument("--fstop",   dest="fstop",       metavar="GIGAHERTZ",    default=DEFAULT_FSTOP,      type=float, help="Sweep stop frequency")
    argparser.add_argument("--tsweep",  dest="tsweep",      metavar="MILLISECONDS", default=DEFAULT_TSWEEP,     type=float, help="Sweep duration")
    argparser.add_argument("--nsweeps", dest="nsweeps",     metavar="NO. SWEEPS",   default=DEFAULT_NSWEEPS,    type=int,   help="Number of sweeps to perform")
    argparser.add_argument("--tperiod", dest="tperiod",     metavar="MILLISECONDS", default=DEFAULT_TPERIOD,    type=float, help="Time period between successive sweeps")
    argparser.add_argument("--sweepmode", dest="sweepmode", choices=[mode.name for mode in SenseX1000.SweepMode], default=DEFAULT_SWEEPMODE, help="Sweep mode")
    args = argparser.parse_args()

    # Set up logging as requested by number of -v switches
    loglevel = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
    logging.basicConfig(stream=sys.stderr, level=loglevel[args.verbose], format='%(asctime)s %(levelname)-8s %(message)s')
    logger.setLevel(logging.INFO)

    # Look for X1000 series devices
    devices = SenseX1000.find_devices()

    logger.info('Devices found connected to system:')
    for device in devices:
        logger.info(f'  - {device.resource_name}')

    if len(devices) == 0:
        logger.error('No Sense X1000 devices found')
        return 2

    with SenseX1000.open_device(devices[0]) as device:
        logger.info(f'Connected to SCPI Resource {devices[0].resource_name}')

        # Recall preset and clear registers
        device.core.rst()
        device.core.cls()

        logger.info(f'*IDN?: {device.core.idn()}')

        # Print some device information
        info = device.system.info()
        logger.info(f'HWTYPE: {info["HWTYPE"]}')
        logger.info(f'HWREVISION: {info["HWREVISION"]}')
        logger.info(f'ID: {info["ID"]}')
        logger.info(f'POWER:CURRENT: {info["POWER"]["CURRENT"]}')
        logger.info(f'POWER:VOLTAGE: {info["POWER"]["VOLTAGE"]}')
        logger.info(f'POWER:SOURCE: {info["POWER"]["SOURCE"]}')
        logger.info(f'ROSCILLATOR:DCTCXO: {info["ROSCILLATOR"]["DCTCXO"]}')
        logger.info(f'ROSCILLATOR:ENABLED: {info["ROSCILLATOR"]["ENABLED"]}')
        logger.info(f'ROSCILLATOR:HOLDOVER: {info["ROSCILLATOR"]["HOLDOVER"]}')
        logger.info(f'ROSCILLATOR:LOCK: {info["ROSCILLATOR"]["LOCK"]}')
        logger.info(f'ROSCILLATOR:SOURCE: {info["ROSCILLATOR"]["SOURCE"]}')
        logger.info(f'TEMP: {info["TEMP"]}')
        logger.info(f'USB: {info["USB"]}')

        # Configure radar with given configuration
        device.sense.frequency_start(args.fstart * 1E9)
        device.sense.frequency_stop(args.fstop * 1E9)
        device.sense.sweep_time(args.tsweep * 1E-3)
        device.sense.sweep_count(args.nsweeps)
        device.sense.sweep_period(args.tperiod * 1E-3)
        device.sense.sweep_mode(SenseX1000.SweepMode[args.sweepmode])
        device.calc.trace_list([0])

        # Dump a configuration object with all configured settings
        config = device.sense.dump()
        logger.info(f'Configuration: {config}')

        # Print some useful status information
        logger.info(f'Aux PLL Lock: {device.control.radar_auxpll_locked()}')
        logger.info(f'Main PLL Lock: {device.control.radar_mainpll_locked()}')
        logger.info(f'Ref. Osc. Source: {device.sense.refosc_source_current()}')
        logger.info(f'Ref. Osc. Status: {device.sense.refosc_status()}')

        # Run acqusition/read/plot loop until ctrl+c requested

        while not close:
            start = time.time()
            # Perform sweep
            logger.info('+ Running sweep(s)')
            acq = device.initiate.immediate_and_receive()

            # Read all data in one go
            logger.info('  Read data')
            data = acq.read()

            # Perform processing and plotting
            logger.info('  Plotting')
            plot(config, data)

            stop = time.time()
            logger.info(f'Time taken: {stop-start:.3f} sec. (FPS: {1/(stop-start):.1f})')
    return 0


if __name__ == "__main__":
    # Call main function above
    sys.exit(main())
