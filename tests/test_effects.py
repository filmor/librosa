#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''Unit tests for the effects module'''

# Disable cache
import os
try:
    os.environ.pop('LIBROSA_CACHE_DIR')
except KeyError:
    pass

from nose.tools import raises, eq_

import matplotlib
matplotlib.use('Agg')
import librosa
import numpy as np

__EXAMPLE_FILE = 'data/test1_22050.wav'


def test_time_stretch():

    def __test(infile, rate):
        y, sr = librosa.load(infile, duration=4.0)
        ys = librosa.effects.time_stretch(y, rate)

        orig_duration = librosa.get_duration(y, sr=sr)
        new_duration = librosa.get_duration(ys, sr=sr)

        # We don't have to be too precise here, since this goes through an STFT
        assert np.allclose(orig_duration, rate * new_duration,
                           rtol=1e-2, atol=1e-3)

    for rate in [0.25, 0.5, 1.0, 2.0, 4.0]:
        yield __test, 'data/test1_22050.wav', rate

    for rate in [-1, 0]:
        yield raises(ValueError)(__test), 'data/test1_22050.wav', rate


def test_pitch_shift():

    def __test(infile, n_steps, bins_per_octave):
        y, sr = librosa.load(infile, duration=4.0)
        ys = librosa.effects.pitch_shift(y, sr, n_steps,
                                         bins_per_octave=bins_per_octave)

        orig_duration = librosa.get_duration(y, sr=sr)
        new_duration = librosa.get_duration(ys, sr=sr)

        # We don't have to be too precise here, since this goes through an STFT
        eq_(orig_duration, new_duration)

    for n_steps in np.linspace(-1.5, 1.5, 5):
        for bins_per_octave in [12, 24]:
            yield __test, 'data/test1_22050.wav', n_steps, bins_per_octave

    for bins_per_octave in [-1, 0]:
        yield (raises(ValueError)(__test), 'data/test1_22050.wav',
               1, bins_per_octave)


def test_remix_mono():

    # without zc alignment
    y = np.asarray([1, 1, -1, -1, 2, 2, -1, -1, 1, 1])
    y_t = np.asarray([-1, -1, -1, -1, 1, 1, 1, 1, 2, 2])
    intervals = np.asarray([[2, 4],
                            [6, 8],
                            [0, 2],
                            [8, 10],
                            [4, 6]])

    def __test(y, y_t, intervals, align_zeros):
        y_out = librosa.effects.remix(y, intervals,
                                      align_zeros=align_zeros)
        assert np.allclose(y_out, y_t)

    for align_zeros in [False, True]:
        yield __test, y, y_t, intervals, align_zeros


def test_remix_stereo():

    # without zc alignment
    y = np.asarray([1, 1, -1, -1, 2, 2, -1, -1, 1, 1])
    y_t = np.asarray([-1, -1, -1, -1, 1, 1, 1, 1, 2, 2])
    y = np.vstack([y, y])
    y_t = np.vstack([y_t, y_t])

    intervals = np.asarray([[2, 4],
                            [6, 8],
                            [0, 2],
                            [8, 10],
                            [4, 6]])

    def __test(y, y_t, intervals, align_zeros):
        y_out = librosa.effects.remix(y, intervals,
                                      align_zeros=align_zeros)
        assert np.allclose(y_out, y_t), str(y_out)

    for align_zeros in [False, True]:
        yield __test, y, y_t, intervals, align_zeros


def test_hpss():

    y, sr = librosa.load(__EXAMPLE_FILE)

    y_harm, y_perc = librosa.effects.hpss(y)

    # Make sure that the residual energy is generally small
    y_residual = y - y_harm - y_perc

    rms_orig = librosa.feature.rmse(y=y)
    rms_res = librosa.feature.rmse(y=y_residual)

    assert np.percentile(rms_orig, 0.01) > np.percentile(rms_res, 0.99)


def test_percussive():

    y, sr = librosa.load('data/test1_22050.wav')

    yh1, yp1 = librosa.effects.hpss(y)

    yp2 = librosa.effects.percussive(y)

    assert np.allclose(yp1, yp2)


def test_harmonic():

    y, sr = librosa.load('data/test1_22050.wav')

    yh1, yp1 = librosa.effects.hpss(y)

    yh2 = librosa.effects.harmonic(y)

    assert np.allclose(yh1, yh2)
