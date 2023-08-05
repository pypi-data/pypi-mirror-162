# Speech Quefrency Transform (SQT)

The efficient use of a communication bandwidth starts with the data source. The features of the speech signals can be extracted and reconstructed to lower the Internet traffic of the acoustic artificial agents and increase the quality of the automatic speech recognition systems. The Speech Quefrency Transform (SQT) is hereby introduced in the work to enrich the communication space between the artificial agents and mankind. We describe the motivation, methodology, and deep learning approach in detail as we apply the SQT technology to several applications: sharp pitch track extraction, real-time speech communications, and emotion recognition. Combining multiple processes, attenuating background noises, and enabling distant-speech recognition, we introduce the SQT cepstrograms as well as multiple quefrency scales. SQT is a set of frequency transforms whose spectral leakages are controlled per a frequency-modulation model. SQT captures the stationarity of time series onto a hyperspace that resembles the cepstrogram when it is reduced for pitch track extraction. This library is an interface for Automatic Speech Recognition (ASR) for converting an audio series to and from the cepstral domain. 

## Python

### The Int16 Version

1. Install:
```
pip install sqtpy
```
or 
```
pip install -i https://test.pypi.org/simple/ sqtpy
```

2. Initalize a new instance
```
import sqtpy
sqt = sqtpy.SQT( N = 500 , Rs = 300 , Fs = 8000 )
```

3. Extract Pitch Track and speech features
```
[F0, Hm, Et] = sqt.encode( I0 )
```

4. Estimate the original speech signal from the extracted speech features
```
I = sqt.decode( F0, Hm )
```

Note: there is a Jupyter Notebook demo in the package directory. 

## Acknowledgements:
1. Ahmad Hasanain, Muntaser Syed, Veton Kepuska, Marius Cilaghi, "Speech Quefrency Transform" - 2019, ResearchSqaure.
2. Veton Z Kepuska, "Wake-up-word speech recognition application for first responder communication enhancement" - 2006, Florida Institute of Technology (WUW-I Speech Corpus) 
3. Minnesota Department of Health, "4 - Baby Behavior: Crying baby" - 2017, Youtube.
