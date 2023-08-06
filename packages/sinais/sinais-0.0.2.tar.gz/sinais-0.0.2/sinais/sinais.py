# Author: Rafael do Nascimento Pereira <rnp@25ghz.net>
#

from fxpmath import Fxp
import numpy as np
import plotly.graph_objects as go    # for data visualisation
#import plotly.io as pio              # to set shahin plot layout


def gen_sinewave(freq=100, samp_rate=5000, plot=False, save=False):
    '''
    Generate a sine with a given frequency and sampling rate

    Parameters
    ----------
    freq: int
        sine wave frequency in Hertz
    sampe:rate: int
        sampling rate used to generate the sine wave
    plot: boolean
        if True, plots the geneated sine wave
    save: boolean
        if True, saves the generated sinve wave into a file

    Returns
    -------
    None
    '''
    sample_rate = samp_rate
    frequency   = freq
    amplitude   = 1

    time     = np.arange(0, 0.2, 1/sample_rate);
    sinewave = np.empty(len(time))

    sinewave = amplitude*np.sin(2*np.pi*frequency*time)

    if plot is True:
        fig = go.Figure(layout=dict(xaxis=dict(title='Time (s)'),yaxis=dict(title='Amplitude (V)')))
        fig.add_scatter(x=time, y=sinewave)
        fig.show()

    if save is True:
        pass


def gen_sinewave_noisy(freq=100, samp_rate=5000, plot=True, save=False):
    '''
    Generate a sine with a given frequency and sampling rate

    Parameters
    ----------
    freq: int
        sine wave frequency in Hertz
    sampe_rate: int
        sampling rate used to generate the sine wave
    plot: boolean
        if True, plots the geneated sine wave
    save: boolean
        if True, saves the generated sinve wave into a file

    Returns
    -------
    sinawave_noisy : NDArray
        noisy sine wave

    '''
    sample_rate = samp_rate
    frequency   = freq
    amplitude   = 1

    # Get x values of the sine wave
    time     = np.arange(0, 0.2, 1/sample_rate);
    sinewave = np.empty(len(time))

    # Amplitude of the sine wave is sine of a variable like time
    x = np.linspace(-np.pi, np.pi, len(time))

    sinewave = amplitude*np.sin(2*np.pi*frequency*time)

    sinewave_noisy = sinewave + 0.05*np.random.randn(len(time))

    td_dataFile = open('sine_1f.txt', 'wt')
    np.savetxt(td_dataFile, time, fmt='%10.10f', delimiter=' ', newline='\n')

    td_dataFile_noisy = open('sine_1f_noisy.txt', 'wt')
    np.savetxt(td_dataFile_noisy, time, fmt='%10.10f', delimiter=' ', newline='\n')

    if plot is True:
        fig = go.Figure(layout=dict(xaxis=dict(title='Time (s)'),yaxis=dict(title='Amplitude (V)')))
        fig.add_scatter(x=time, y=sinewave)
        fig.add_scatter(x=time, y=sinewave_noisy)
        fig.show()

    if save is True:
        pass

    #self.gen_mov_avg(sinewave_noisy, time, 10)

    return sinewave_noisy


def gen_mov_avg(signal, time, ntaps = 5):
    '''
    Generate a moving average filtered signal from the input signal

    Parameters
    ----------
    signal: NDArray

    time: NDArray

    ntaps: int

    Returns
    --------

    '''

    mov_avg = np.convolve(signal, np.ones(ntaps),'valid') / ntaps

    fig = go.Figure(layout=dict(xaxis=dict(title='Time (s)'),yaxis=dict(title='Amplitude (V)')))
    fig.add_scatter(x=time, y=signal)
    fig.add_scatter(x=time, y=mov_avg)
    fig.show()

    return mov_avg


def save_fxp(signal, format='fxp-s16/15', fname='./signal_fp.txt'):
    """
    Save data in the given format using Fxp math

    Parameters
    ----------
    signal: NDArray

    Returns
    -------
    None
    """

    n_fxp = Fxp(signal, format)

    with open(fname, 'w') as f:
        for fp in n_fxp:
            f.write(str(fp.bin(frac_dot=False)))
            f.write('\n')


def load_fxp(signal, format='fxp-s16/15', fname='./signal_fp.txt'):
    """
    Parameters
    ----------
    signal: NDArray

    Returns
    -------
    """
    fp = Fxp(dtype=format)

    with open(fname, 'r') as f:
        for i in f:
            print(str(fp.bin(frac_dot=True)))
#            f.read(str(fp.bin(frac_dot=True)))

    return fp

