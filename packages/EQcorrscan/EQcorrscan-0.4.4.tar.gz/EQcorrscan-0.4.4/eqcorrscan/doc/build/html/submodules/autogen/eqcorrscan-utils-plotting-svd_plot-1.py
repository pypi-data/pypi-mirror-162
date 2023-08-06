from obspy import read
import glob, os
from eqcorrscan.utils.plotting import svd_plot
from eqcorrscan.utils.clustering import svd, svd_to_stream
wavefiles = glob.glob(os.path.realpath('../../..') +
                     '/tests/test_data/WAV/TEST_/2013-*')
streams = [read(w) for w in wavefiles[1:10]]
stream_list = []
for st in streams:
    tr = st.select(station='GCSZ', channel='EHZ')
    st.detrend('simple').resample(100).filter('bandpass', freqmin=5,
                                              freqmax=40)
    stream_list.append(tr)
svec, sval, uvec, stachans = svd(stream_list=stream_list)
svstreams = svd_to_stream(uvectors=uvec, stachans=stachans, k=3,
                          sampling_rate=100)
svd_plot(svstreams=svstreams, svalues=sval,
         stachans=stachans)