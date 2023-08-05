""" Some helpfull mathematical functions for analysing data in SciChannels and SciStreams
Copyright Nanosurf AG 2021
License - MIT
"""
import enum
import math
import numpy as np
import scipy.signal
import statistics as stat 
import nanosurf.lib.datatypes.sci_channel as ch
import nanosurf.lib.datatypes.sci_stream as ss

def find_peaks(stream: ss.SciStream, channel_index: int = 0, **kwargs) -> ss.SciStream:
    """ Find all peaks in a stream's channel. e.g amplitude peaks in a frq-spectrum.
    It is based on scipy.signal.find_peaks() for detailed documentation  
    
    Returns
    -------
    SciStream : 
        x-data contains the x positions of the peaks
        data stream contains the y positions of the peaks
    """
    data_channel = stream.get_channel(channel_index)
    peak_indexes, _ = scipy.signal.find_peaks(data_channel.value, **kwargs)    
    max_x_array = np.empty(len(peak_indexes))
    max_y_array = np.empty_like(max_x_array)
    for idx, peak_index in enumerate(peak_indexes):
        max_x_array[idx] = stream.x.value[peak_index]
        max_y_array[idx] = data_channel.value[peak_index]
    
    # create resulting stream
    result = ss.SciStream(channels=1)
    result.x = ch.SciChannel(copy_from=max_x_array, unit=stream.x.unit)
    result.channels[0] = ch.SciChannel(copy_from=max_y_array, unit=data_channel.unit)
    return result

def find_highest_peak(stream: ss.SciStream, channel_index: int = 0, **kwargs) -> tuple:
    """ Returns the highest peak in a data channel.
    
    Returns
    -------
    tuple : (bool, x, y)
        First boolean  indicates if a peak could be detected
        If True, then x, y is the coordinate of the peak
    """
    peaks = find_peaks(stream, channel_index, **kwargs)
    if peaks.get_stream_length() >= 1:
        max_indexes = np.where(peaks.channels[0].value == np.amax(peaks.channels[0].value))
        highest_peak_index = int(max_indexes[0])
        return (True, peaks.x.value[highest_peak_index], peaks.channels[0].value[highest_peak_index])
    else:
        return (False, 0, 0)

def calc_poly_fit(stream: ss.SciStream, channel_index: int = 0, degree: int = 1) -> np.ndarray:
    """ Calculates a polynominal fit of a data channel.
    It is a non exception throwing version of numpy's np.polyfit(). See detailed function description there
    
    Results
    -------
    fir_param : ndarray
        either the result of the poly_fit or an array with size = 0
    """
    try:
        fit_param = np.polyfit(stream.x.value, stream.channels[channel_index].value, deg=degree)
    except :
        fit_param = np.array([]) 
    return fit_param

class fft_window_type(enum.Enum): 
    uniform = enum.auto()   # no windowing (all coefficient are 1.0)
    hanning = enum.auto()   # windowing function usefull for noise and single frequencies (amplitude most accurate but broader spectrum)
    hamming = enum.auto()   # windowing function usefull for signals with many frequency components (amplitude not so accurate but higher resolution)
    blackman = enum.auto()

def calc_fft(data_samples: ch.SciChannel, samplerate: float, window: fft_window_type = fft_window_type.hanning, powerspectrum: bool = False) -> ss.SciStream:
    """ calculate amplitude or spectral density spectrum from time data array(s) 
    
    Parameters
    ----------
    data_samples: SciChannel
        A array of data points sampled at equally time differences 
    samplerate: float
        defines how fast data points where measured. Provided in [Hz]   
    window: optional, fft_window_type
        defines the data windowing function to be used. Available functions are defined in enum fft_window_type 
    powerspectrum: optional, bool
        if True then the spectrum is normalized by the frequency resolution and the resulting unit is 1/sqrt(Hz)

    Result
    ------
        DataChannel
            Spectrum as SciStream  
    """

    n_samples = data_samples.value.shape[0]

    #prepare result arrays--------------------------
    n_fft_points = int(n_samples/2+1)

    fft_result_array = np.zeros(n_fft_points)

    # define FFT windowing --------------------------------
    if window == fft_window_type.uniform:
        s_window_array = np.ones(n_samples)
        noise_power_bandwidth = 1.0

    elif window == fft_window_type.hanning:
        s_window_array = np.hanning(n_samples)/0.5
        noise_power_bandwidth = 1.5

    elif window == fft_window_type.hamming:
        s_window_array = np.hamming(n_samples)/0.54
        noise_power_bandwidth = 1.36

    elif window == fft_window_type.blackman:
        s_window_array = np.blackman(n_samples)
        noise_power_bandwidth = 1.73
    else:
        print("calc_frq_spectrum: Error: unknown windowing function selected."+str(window))
        return ss.SciStream()
    
    # calculate FFT spectrums --------------------------------
    fft_data_array = np.fft.fft(s_window_array * data_samples.value)
    fft_amp_array = np.abs(fft_data_array[:n_fft_points]) / n_fft_points

    # convert to power spectrum if needed
    if powerspectrum:
        fft_result_array = fft_amp_array / np.sqrt(samplerate / n_fft_points * noise_power_bandwidth)
    else:
        fft_result_array = fft_amp_array

    # create X-Axis vector with frequencies
    if samplerate > 0.0:
        fft_frequency_array = np.linspace(0.0, samplerate/2.0, n_fft_points, endpoint=True)
    else:
        fft_frequency_array = np.linspace(0.0, n_fft_points, 1.0, endpoint=False)

    # assemble the resulting FFT spectrum as SciStream
    result = ss.SciStream((fft_frequency_array, fft_result_array))
    result.x.unit = "Hz"
    if powerspectrum:
        result.channels[0].unit = f"{data_samples.unit}/sqrt(Hz)"
    else:
        result.channels[0].unit = data_samples.unit
    return result

def create_compress_log_spectrum_max(spec_data: ss.SciStream, channel_index: int = 0, min_dist_factor=1.02) -> ss.SciStream:
    """Reduces number of data points in large data sets by logarithmic compression method
        uses the max value over all values compressed 
        Has good amplitude accuracy but show larger noise floor
    
    Parameters
    ----------
    spec_data: DataArray
        original spectum to be compressed
    min_dist_factor
        defines the minimal distance of two frq_array points must have to compress these. Distance > frq_array[i]/frq_array[i-1] 
    
    Result
    ------
        compressed_data_channel: SciStream
            new compressed array of frequency data points, not equally spaced anymore
    """
    
    datalen = spec_data.get_stream_length()
    compressed_frq_array = spec_data.get_channel(channel_index).value.tolist()[0:2]
    compressed_spectrum_array=spec_data.get_stream_range().value.tolist()[0:2]

    lastindex=1 

    for i in range(2,datalen):
        frq_data = spec_data.get_stream_range().value
        amp_data = spec_data.get_channel(channel_index).value
        if frq_data[i]/frq_data[lastindex] >= min_dist_factor:
            compressed_frq_array.append(stat.mean(frq_data[(lastindex+1):(i+1)]))
            compressed_spectrum_array.append(amp_data[(lastindex+1):(i+1)].max())
            lastindex = i

    compressed_frq = ch.SciChannel(compressed_frq_array, unit=spec_data.get_stream_unit())
    compressed_amp = ch.SciChannel(compressed_spectrum_array, unit=spec_data.get_channel_unit(channel_index))

    result = ss.SciStream(compressed_frq, channels=1)
    result.set_channel(0, compressed_amp)
    return result

def create_compress_log_spectrum_mean(spec_data: ss.SciStream, channel_index: int = 0, min_dist_factor=1.02) -> ss.SciStream:
    """Reduces number of data points in large data sets by logarithmic compression method
        uses the mean value over all values compressed 
        Has good amplitude accuracy but show larger noise floor
    
    Parameters
    ----------
    spec_data: DataArray
        original spectum to be compressed
    min_dist_factor
        defines the minimal distance of two frq_array points must have to compress these. Distance > frq_array[i]/frq_array[i-1] 
    
    Result
    ------
        compressed_data_channel: SciStream
            new compressed array of frequency data points, not equally spaced anymore
    """
    datalen = spec_data.get_stream_length()
    compressed_frq_array = spec_data.get_channel(channel_index).value.tolist()[0:2]
    compressed_spectrum_array=spec_data.get_stream_range().value.tolist()[0:2]

    lastindex=1 # last position in *data, that was included in calculation of filt_...
    
    for i in range(2,datalen):
        frq_data = spec_data.get_stream_range().value
        amp_data = spec_data.get_channel(channel_index).value
        if frq_data[i]/frq_data[lastindex] >= min_dist_factor:
            compressed_frq_array.append(stat.mean(frq_data[(lastindex+1):(i+1)]))
            compressed_spectrum_array.append(stat.mean(amp_data[(lastindex+1):(i+1)]))
            lastindex = i

    compressed_frq = ch.SciChannel(compressed_frq_array, unit=spec_data.get_stream_unit())
    compressed_amp = ch.SciChannel(compressed_spectrum_array, unit=spec_data.get_channel_unit(channel_index))

    result = ss.SciStream(compressed_frq, channels=1)
    result.set_channel(0, compressed_amp)
    return result

def remove_peaks_in_spectrum(spec_data: ss.SciStream, channel_index: int = 0, frq_peaks: list[float] = [], span=1) -> ss.SciStream:
    """removes peaks at certain frequencys 
    
    Parameter
    ---------
    spec_data: SciStream
        The original spectrum
    channel_index: int
        The channel to smooth out
    frq_peaks: list[float]
        array of frequencys to be smoothed out
    span              
        defined as number of freqency index left and right of the peak to be used to smooth out the peak
    
    Returns
    -------
    smoothed_spec: SciStream
    """ 
    result = ss.SciStream(spec_data)
    for frq in frq_peaks:
        peak_ind = np.where(spec_data.x.value >= frq)[0][0]
        
        for smooth_index in range(peak_ind-span,peak_ind+span):
            result.channels[channel_index].value[smooth_index] = result.channels[channel_index].value[smooth_index+span*2+1]
    return result

def get_total_harmonic_distortion(spec_data: ss.SciStream, channel_index: int = 0, fundamental_frequency: float = 0.0, max_number_of_harmonics: int = 0) -> float:
    """ calculates the distortion of a signal by measuring its harmonics 
    
    Parameters
    ----------
    spec_data: SciStream
        The data source 
    channel_index: int
        The data source  channel to analyse
    fundamental_frequency
        the fundamental frequency from which the THD calculation shall be done. Defined in [Hz]. The nearest frq found in the frq_array is used 
    max_number_of_harmonics 
        optional, limits the number of harmonic frequency to used for THD calculation, 0 defines to use all possible harmonics found in the spectrum
    
    Result
    ------  
        thd - distortion in [dB]
    """ 
    ind = np.where(spec_data.x.value >= fundamental_frequency)[0][0]
    list_of_harmonics = range(ind*2, len(spec_data.x.value), ind)
    if max_number_of_harmonics > 0:
        list_of_harmonics = list_of_harmonics[:max_number_of_harmonics] # limit number of harmonics to be measured

    thd = 20.0 * math.log10(np.sqrt(sum(spec_data.channels[channel_index].value[list_of_harmonics]**2))/spec_data.channels[channel_index].value[ind])
    return thd

def get_noise_floor(spec_data: ss.SciStream, channel_index: int = 0, one_over_f_edge_frq: float = 0.0, level_of_percentile: float = 50.0, res_noise_floor_spec: ss.SciStream = None) -> float:
    """ determine the noise floor of a spectrum.
    
    With the level_of_percentie one can define the amount of spike and noise hills to be suppressed.
    With a value of 50 in most cases the background noise is returned. 
    With 100 maximal value found in the spectrum is returned
    With 80-95 small spikes (50Hz or so) can be ignored but real unexpected noise increase is detected

    Can be nicely combined with the function "create_compress_log_spectrum_mean()" to improve result

    Parameter
    ---------
    spec_data: SciStream
        The data source 
    channel_index: int
        The data source  channel to analyse
    one_over_f_edge_frq:  optional
        if defined compensate for 1/f noise increase below edge frequency. Defined in [Hz]. 
    level_of_percentile:  optional
        defines the amount of data to be inside the noise_level. Usefull to compensate for spikes. Has to be from 1-100 [%]. 
    res_noise_floor_spec: optional
        if defined the used spectrum for noise_floor calculation is returned. Usefull to check for 1/f compensation
    
    Result
    ------  
    noise_level:
        noise level found 
    """ 
    # compensate for 1/f noise increase below edge frequency
    if one_over_f_edge_frq > 0.0:
        # # scale 1/f noise below frequency point
        low_data_array = spec_data.channels[channel_index].value[spec_data.x.value < one_over_f_edge_frq]
        low_frq_array  = spec_data.x.value[spec_data.x.value < one_over_f_edge_frq]
    
        low_data_array = low_data_array * np.sqrt(low_frq_array) / np.sqrt(one_over_f_edge_frq)
    
        low_data_array = low_data_array[2:] # remove DC
        low_frq_array  = low_frq_array[2:]
        
        res_data_array = np.concatenate((low_data_array, spec_data.channels[channel_index].value[len(low_data_array):]))
    else:
        res_data_array = spec_data.channels[channel_index].value

    noise_floor = np.percentile(res_data_array, level_of_percentile)

    if isinstance(res_noise_floor_spec, ss.SciStream):
        res_noise_floor_spec.channels[0].value = res_data_array
        res_noise_floor_spec.x.value = spec_data.x.value
    return noise_floor

def get_amplitude(spec_data: ss.SciStream, channel_index: int = 0, frq: float = 0.0):
    """ returns the amplitude value of a specified frequency
        The amplitude value of the closest frequency found in the array is returned         
    
    Parameter
    ---------
    spec_data: SciStream
        The data source 
    channel_index: int
        The data source  channel to analyse
    frq : float
        the frequency of interest in [Hz]

    Result
    ------
    (amplitude, found_index): tuple(float, int)
        The amplitude of the data array at nearest frq
        found_index, the position index in data array. If not found, index is negativ
    """ 
    found_index = -1
    
    ind = np.where(spec_data.x.value >= frq)
    found_any = ind[0].shape[0]
    
    if found_any > 0:
        found_index = ind[0][0]
    
    if found_index >= 0:
        amp = spec_data.channels[channel_index].value[found_index]
    else:
        amp = 0.0
    return (amp, found_index)
