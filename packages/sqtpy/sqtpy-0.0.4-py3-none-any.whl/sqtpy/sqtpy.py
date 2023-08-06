# The SQT Int16 Version
# Authored by by Ahmad Hasanain
# revised by Muntaser Syed
# supervised by Dr Veton Kepuska
# AhmadZuhair.com © 2022



import numpy as np
import pickle as pk
import os, inspect


class SQT:
    '''

# The Speech Quefrency Transform (SQT) Python Library

This is an Automatic Speech Recognition (ASR) interface that converts speech audio to and from the cepstral domain. In other words, it extracts the locally stationary speech featuers from the speech signals, and it reconstructs them back to speech singals. It represents the speech series by two features and has several applications. 

### Speech Featrues:
1. Pitch Tracks
2. Responsive-Band Spectrograms (harmonic series). 
    
### Quefrency Scales:
1. Linear-Space
2. Reciprocal (this is similar to the MFCC scale)
3. Geometrical (this is based on the two dimensional view of the pitch function)

### Applications:
1. Speech Analysis and Synthesis 
2. Natural Language Processing (NLP)
3. Machine Learning (ML)
4. Telecommunications
    
    
## Homepage:
https://github.com/hasanainaz/sqt
    '''
    

    
    def __init__(self, Fs=8000, M=32, N=50, Fmax=880, Fmin=90, Rs=30, scale='geo', lifter = 1, smooth=0 , gamma = 2, name = "newInterface" ):  
        '''
        # The SQT Initializer:
        
        Initialize an interface instance of the Speech Quefrency Transform (SQT) class. In this int16 light version, all input parameters are positve integers that are less than 32,767.
        
        ## Parameters:
        Fs: sampling rate in Hertz
        M: spectral resolution or harmonic order
        N: cepstral resolution or pitch/quefrency size
        Fmax: maximum quefrency
        Fmin: minimum quefrency
        Rs: the output frame rate: 24, 30, 120, 480.
        scale: lin, rec, or geo (default) 
        smooth: widnow length of a moving average filter (default: 0)
        gamma: 2, 4, or 6
        
        ## Return:
        an SQT interface instance.    
        
        '''
        
#         print("Notebook Demo is at: ")
#         import os
#         dir_path = os.path.dirname(os.path.realpath(__file__))
#         print(dir_path)
        
        # parameters
        self.Fs = np.int(Fs) # sampling rate
        self.M = np.int( M ) # sepctral resolution, 
        self.N = np.int( N ) # cepstral resolution, pitch, or quefrency
        self.Fmax = Fmax # maximum quefrency, pitch 
        self.Fmin = Fmin # minimum quefrency, pitch 
        self.Rs = Rs # frame rate
        self.name = name # Interface refrence
        self.gam = np.int(gamma) # number of cycles: 2, 4, or 6
        self.smooth = np.int(smooth)
        self.lifter = np.int(lifter)
        
        # fixed
        self.c = np.int( Fs * self.gam / Fmin / 2 ) # window size (samples)
        self.clen = 2*self.c+1 # the c is an even number for centering
        self.s = np.int( Fs / Rs ) # step size (samples)
        self.Rs = Fs / self.s # actual frame rate
#         print( 'Frame Rate: ', self.Rs )
        self.d = np.int(2) # complex mode
        self.ma = np.int(1) # the multiplitive adjustment for int16 is 181

        # Initiate Quefrency Scale
        scale = scale.lower()
        if scale in ['lin','linear']:
            self.R =  np.linspace(  Fmin , Fmax , N ) #.astype( np.int16 )
        elif scale in ['rec','reciprocal']:
            self.R =  1. / np.linspace( 1. /  Fmin , 1. / Fmax , N ) #.astype( np.int16 )
        else: # scale in ['geo', 'geometrical']
            self.R = ( Fmin * ( Fmax / Fmin ) ** ( np.arange(N) / (N-1) ) ) #.astype( np.int16 )
        
        # Initiate Quefrency Transform
        [u,n,m,k,w] = np.mgrid[ -self.c:self.c+1, 0:N , 0:M , 0:2 , 0:self.d ]
        fi = self.R[n] / Fs * ( 1. + m - k * 0.5 )
        Ti = Fs / self.R[n] * self.gam / 2
        w0 = np.pi / self.d
        T = 1.*(fi<=0.5)*(np.abs(u)<=Ti)*np.cos(2.*np.pi*u*fi-w*w0) / Ti * self.ma
        self.T = np.reshape( T , (self.clen,-1) , order='F') ;
#         self.T = (self.T* self.ma ).astype( np.int16 )
        
        self.Ti = Ti
        self.xlen = -1
        self.data_dir = inspect.getfile(self.__class__).replace("sqtpy.py","sample_data/")
        
        
    def encode( self, I ):
        '''
        # Input
        I: a mono channel/dimension array of speech audio
        
        # Returns
        F0: pitch track (in Hz)
        Hm: harmonic energies
        Et: expected energy
        
        
        '''
        
        # Normalize Series
        I = I[:]
        I[np.isnan(I)] = 0
        I = I / np.amax( np.abs(I) )
#         I = I * self.ma
#         I = I.astype( np.int16 )
        
        # Extract Frames
        if len(I)!=self.xlen: # this caches the sliding frame indices if not available
            self.xlen=len(I)
            cY,cX=np.meshgrid(np.arange(self.clen)-self.c, 
                              np.arange(1+np.ceil(self.xlen/self.s))*self.s)
            self.cIn=(cX+cY).astype(int) # indices 
            self.cIn[self.cIn<0]=0 # left edge padding
            self.cIn[self.cIn>=self.xlen]=self.xlen-1 # right edge padding
        I0 = I[self.cIn] # applying the indices of the sliding frame/widnow
        lenI = len(I0) # number of frames
        
        # Calculate Expected RMS Energy
        Et = np.sqrt( np.mean( ( I0 / self.ma )**2 , axis=1) ) 
        
        # Transform Frames
        I0 = np.abs(np.matmul(I0,self.T)) 
        I0 = I0.reshape((lenI,self.N,self.M,2,self.d),order='F')
        
        # Cache Spectrogram
        Hm = np.reshape( I0[:,:,:,0,:] ,(-1,2*self.M),order='F')/ 4 / ( self.ma ** 2 )
          
        # reduce
        I0 =  np.sum(I0,axis=4) # Manhattan distance
        I0 = I0[:,:,:,0] - I0[:,:,:,1] # overtone filtering
        I0[I0<0] = 0 # rectify
        
        # filter
        for i in range(self.lifter):
            if i % 2 == 0:
                I0[:,:,:-1] = ( I0[:,:,:-1] * I0[:,:,1:] ) ** 0.5
            else:
                I0[:,:,1:] = ( I0[:,:,:-1] * I0[:,:,1:] ) ** 0.5
     
        # smooth
        for i in range(self.smooth):
            if i % 2 == 0:
                I0[1:] = ( I0[:-1] + I0[1:] ) * 0.5
            else:
                I0[:-1] = ( I0[:-1] + I0[1:] ) * 0.5
            
    
        # liftered cepstrum
        I0 = np.mean(  I0 , axis=2 )     
        
        # extract 
        n = np.argmax( I0 , axis=1 )
        F0 = self.R[n]
        Hm = Hm[ range( lenI ) + lenI * n  , : ]
        
        self.Q = I0 # cache liftered cepstrogram
        self.n = n # cache pitch track (in unit index)

        return F0, Hm, Et

    def decode(self,F0,Hm):
        
        F0s = []
        Hms = []
        
        for i in range(len(F0)-1):
            F0s.append( np.linspace(F0[i],F0[i+1],self.s) )
            Hms.append( np.linspace(Hm[i],Hm[i+1],self.s) )

        F0s = np.concatenate( F0s )
        Hms = np.concatenate( Hms )
        F0s = np.cumsum( F0s[:,np.newaxis] , axis=0 )
        m = 1 + np.arange(self.M).T
        
        # prodcue
        phase_shift = 0 # np.pi/8
        I = Hms[:,self.M:] * np.cos( 2*np.pi * m * F0s / self.Fs - phase_shift )
        I = I + Hms[:,:self.M] * np.sin( 2*np.pi * m * F0s / self.Fs - phase_shift )
                
        I = np.sum( I , 1 ) * 4 # / self.ma
                
        return I
    
    
    def save(self):
        '''This saves the instance configuraitons by its name'''
        pk.dump( self , open( self.name + ".sqt.pk" , 'wb') )
        print( str(self.name) + " saved." )
    
    def load(name):
        '''This loads the instance configuraitons by its name'''
        return pk.load( open( name + ".sqt.pk" , 'rb')  )
        

class SQTint16:
    '''
We prepared this version of the sqt library for the Raspberry Pi combatablity. This version prioritizes space over speed and quality. In this vesrion, 256-level variables are multiplied while they are in 16-bit-integer-data type, and its temporal and cepstral filterings are done sequantally inside for-loops, so low-order filtering is sticktly recommened in this version.
    '''
    
    def __init__(self, Fs=8000, M=32, N=50, Fmax=880, Fmin=90, Rs=30, scale='geo', lifter = 1, smooth=0 , gamma = 2, name = "newInterface" ):  
        '''
        # The SQT Initializer:
        
        Initialize an interface instance of the Speech Quefrency Transform (SQT) class. In this int16 light version, all input parameters are positve integers that are less than 32,767.
        
        ## Parameters:
        Fs: sampling rate in Hertz
        M: spectral resolution or harmonic order
        N: cepstral resolution or pitch/quefrency size
        Fmax: maximum quefrency
        Fmin: minimum quefrency
        Rs: the output frame rate: 24, 30, 120, 480.
        scale: lin, rec, or geo (default) 
        smooth: widnow length of a moving average filter (default: 0)
        gamma: 2, 4, or 6
        
        ## Return:
        an SQT interface instance.    
        
        '''
        
#         print("Notebook Demo is at: ")
#         import os
#         dir_path = os.path.dirname(os.path.realpath(__file__))
#         print(dir_path)
        
        # parameters
        self.Fs = np.int16(Fs) # sampling rate
        self.M = np.int16( M ) # sepctral resolution, 
        self.N = np.int16( N ) # cepstral resolution, pitch, or quefrency
        self.Fmax = Fmax # maximum quefrency, pitch 
        self.Fmin = Fmin # minimum quefrency, pitch 
        self.Rs = Rs # frame rate
        self.name = name # Interface refrence
        self.gam = np.int16(gamma) # number of cycles: 2, 4, or 6
        self.smooth = np.int16(smooth)
        self.lifter = np.int16(lifter)
        
        # fixed
        self.c = np.int16( Fs * self.gam / Fmin / 2 ) # window size (samples)
        self.clen = 2*self.c+1 # the c is an even number for centering
        self.s = np.int16( Fs / Rs ) # step size (samples)
        self.Rs = Fs / self.s # actual frame rate
#         print( 'Frame Rate: ', self.Rs )
        self.d = np.int16(2) # complex mode
        self.ma = np.int16(181) # the multiplitive adjustment for int16 is 181

        # Initiate Quefrency Scale
        scale = scale.lower()
        if scale in ['lin','linear']:
            self.R =  np.linspace(  Fmin , Fmax , N ).astype( np.int16 )
        elif scale in ['rec','reciprocal']:
            self.R =  1. / np.linspace( 1. /  Fmin , 1. / Fmax , N ).astype( np.int16 )
        else: # scale in ['geo', 'geometrical']
            self.R = ( Fmin * ( Fmax / Fmin ) ** ( np.arange(N) / (N-1) ) ).astype( np.int16 )
        
        # Initiate Quefrency Transform
        [u,n,m,k,w] = np.mgrid[ -self.c:self.c+1, 0:N , 0:M , 0:2 , 0:self.d ]
        fi = self.R[n] / Fs * ( 1. + m - k * 0.5 )
        Ti = Fs / self.R[n] * self.gam / 2
        w0 = np.pi / self.d
        T = 1.*(fi<=0.5)*(np.abs(u)<=Ti)*np.cos(2.*np.pi*u*fi-w*w0) / Ti * self.ma
        self.T = np.reshape( T , (self.clen,-1) , order='F') ;
        self.T = (self.T* self.ma ).astype( np.int16 )
        
        self.Ti = Ti
        self.xlen = -1
        
        
    def encode( self, I ):
        '''
        # Input
        I: a mono channel/dimension array of speech audio
        
        # Returns
        F0: pitch track (in Hz)
        Hm: harmonic energies
        Et: expected energy
        
        
        '''
        
        # Normalize Series
        I = I[:]
        I[np.isnan(I)] = 0
        I = I / np.amax( np.abs(I) )
        I = I * self.ma
        I = I.astype( np.int16 )
        
        # Extract Frames
        if len(I)!=self.xlen: # this caches the sliding frame indices if not available
            self.xlen=len(I)
            cY,cX=np.meshgrid(np.arange(self.clen)-self.c, 
                              np.arange(1+np.ceil(self.xlen/self.s))*self.s)
            self.cIn=(cX+cY).astype(int) # indices 
            self.cIn[self.cIn<0]=0 # left edge padding
            self.cIn[self.cIn>=self.xlen]=self.xlen-1 # right edge padding
        I0 = I[self.cIn] # applying the indices of the sliding frame/widnow
        lenI = len(I0) # number of frames
        
        # Calculate Expected RMS Energy
        Et = np.sqrt( np.mean( ( I0 / self.ma )**2 , axis=1) ) 
        
        # Transform Frames
        I0 = np.abs(np.matmul(I0,self.T)) 
        I0 = I0.reshape((lenI,self.N,self.M,2,self.d),order='F')
        
        # Cache Spectrogram
        Hm = np.reshape( I0[:,:,:,0,:] ,(-1,2*self.M),order='F')/ 4 / ( self.ma ** 2 )
          
        # reduce
        I0 =  np.sum(I0,axis=4) # Manhattan distance
        I0 = I0[:,:,:,0] - I0[:,:,:,1] # overtone filtering
        I0[I0<0] = 0 # rectify
        
        # filter
        for i in range(self.lifter):
            if i % 2 == 0:
                I0[:,:,:-1] = ( I0[:,:,:-1] * I0[:,:,1:] ) ** 0.5
            else:
                I0[:,:,1:] = ( I0[:,:,:-1] * I0[:,:,1:] ) ** 0.5
     
        # smooth
        for i in range(self.smooth):
            if i % 2 == 0:
                I0[1:] = ( I0[:-1] + I0[1:] ) * 0.5
            else:
                I0[:-1] = ( I0[:-1] + I0[1:] ) * 0.5
            
    
        # liftered cepstrum
        I0 = np.mean(  I0 , axis=2 )     
        
        # extract 
        n = np.argmax( I0 , axis=1 )
        F0 = self.R[n]
        Hm = Hm[ range( lenI ) + lenI * n  , : ]
        
        self.Q = I0 # cache liftered cepstrogram
        self.n = n # cache pitch track (in unit index)

        return F0, Hm, Et

    def decode(self,F0,Hm):
        
        F0s = []
        Hms = []
        
        for i in range(len(F0)-1):
            F0s.append( np.linspace(F0[i],F0[i+1],self.s) )
            Hms.append( np.linspace(Hm[i],Hm[i+1],self.s) )

        F0s = np.concatenate( F0s )
        Hms = np.concatenate( Hms )
        F0s = np.cumsum( F0s[:,np.newaxis] , axis=0 )
        m = 1 + np.arange(self.M).T
        
        # prodcue
        phase_shift = 0 # np.pi/8
        I = Hms[:,self.M:] * np.cos( 2*np.pi * m * F0s / self.Fs - phase_shift )
        I = I + Hms[:,:self.M] * np.sin( 2*np.pi * m * F0s / self.Fs - phase_shift )
                
        I = np.sum( I , 1 ) * 4 / self.ma
                
        return I
    
    
    def save(self):
        '''This saves the instance configuraitons by its name'''
        pk.dump( self , open( self.name + ".sqt.pk" , 'wb') )
        print( str(self.name) + " saved." )
    
    def load(name):
        '''This loads the instance configuraitons by its name'''
        return pk.load( open( name + ".sqt.pk" , 'rb')  )
        
        
        
# Misc

def spect(I, cc = 50, s = 100 , fl = 0. , fh = 1., fc = 1. , ec = 1. , figure = False , tf = None , Fs = 8000.  ):
    """ 
    
    # Spectrogram
    
    ## takes: 
    I: input wavefrm of one channel, 
    cc: number of filters - 1, 
    s: downsample size where s = 1 + cc*( 1 - overlapping ) # time downsamling  step

    ## returns: 
    I: 2d spectrogram, 
    tf: transfer filter, 
    Is: signed magnitude of the signal
    
    """
    
#     Fs = 8000.
    res = 2

    if tf is None:
        F, T = np.meshgrid( np.linspace(fl, fh , cc+1) ,  np.arange( 2*cc+1)-cc-1 )
        tf = []
        for i in np.linspace(0., np.pi/2. , res):
            tf.append(np.cos(np.pi * T *  F + i ) )
        tf = np.concatenate( tf , axis = 1)
    
    
    I = enframe( I , (cc, cc) , s ) #, roll=True)
    
    I = I * np.tile( np.sinc( np.linspace(-1, 1, 2*cc+1+2 )  )[1:-1] , (  len(I) , 1 ) )  #**.1
#     I = I * np.tile( scipy.signal.chebwin( 2*cc+1 , at=50)  , (  len(I) , 1 ) )
#     I = I * np.tile( scipy.signal.hann( 2*cc+1 )  , (  len(I) , 1 ) )

#     Plot( (I**2).sum(axis=1) )
    
    R = np.matmul( I, tf ) # transform
    
    I = np.abs(R**2.).reshape( (-1 , res , cc+1) ).sum(axis=1)
    
#     Plot( I.mean(axis=1)  )#/(2*cc+1.) )
#     I = np.log2( I )
#     I = I**.3
    
    if figure:
        import matplotlib.pyplot as plt
        plt.figure()
        plt.imshow(np.rot90(  I**.3  ),cmap = 'binary',aspect = 'auto',interpolation='nearest', extent=[0, len(I) * s / Fs, 0 , Fs/2 ] )
        plt.ylabel(   'Output: Frequency, $Hz$'     )
        plt.xlabel(  'Time, $s$' )
        
    return I


def enframe(I, padding = (3, 3), step = 1, roll = False, inverse = False):
    """ Provides Framing for a Time Sliding Window. / Author: Ahmad
    I: is a 1d array (for time framing) or 2d (when inverse = True)
    step: step size (integer)
    padding = (left, right): padding sizes. Note that ( padding - step) / (1+left+right) ) = the overlapping rate with the adjacent (left, right) steps
    roll: wrap columns if True; otherwise, pad wrapped with zeros
    inverse: (to inverse the output, use the same filter)
    ## Output Example
    I = np.array([1,2,3]); print('forward input (signal)\n', I )
    I = enframe(I, step = 1, padding = (3, 2) ); print('forward output (framed) \n', I )
    I[0,:] +=.1; I[1,:] +=.2; I[2,:] +=.3; print('backward input (rows marked) \n',I)
    I = enframe(I, step = 1, padding = (3, 2), inverse=True); print('backward output (deframed)  \n',I)
    I = np.sum( I , axis = 0)[:np.shape(I)[0]]; print('back summed for the origional input \n',I)
    #  Out[]:
    #            forward input (the signal, three data in an axis)
    #              [1 2 3]
    #             forward output (the framed, three columns added to the left and two to the right) 
    #              [[0. 0. 0. 1. 2. 3.]
    #              [0. 0. 1. 2. 3. 0.]
    #              [0. 1. 2. 3. 0. 0.]]
    #                            ^- the input column
    #             backward input (rows marked) 
    #              [[0.1 0.1 0.1 1.1 2.1 3.1]
    #              [0.2 0.2 1.2 2.2 3.2 0.2]
    #              [0.3 1.3 2.3 3.3 0.3 0.3]]
    #             backward output (deframed) 
    #             [[1.1 2.1 3.1 0.1 0.1 0.1]
    #             [1.2 2.2 3.2 0.2 0.2 0.2]
    #             [1.3 2.3 3.3 0.3 0.3 0.3]]
    #             sum for the origional input 
    #              [3.6 6.6 9.6]
    """
    left, right = padding
    n = np.shape(I)[0]
    n = len(I)
    Y, X = np.meshgrid( np.arange( right + left + 1 ) -left ,  np.arange( np.ceil(n/step) )*step)
    if inverse:
        return I[X,Y-X-1+left-right]
    In =  (X+Y).astype(int)
    if roll:
        In[In<0] %= n
        In[In>=n] %= n
        I = I[In]   
    else:
        I = np.append(I, [0.])
        In[In<0 ] = n
        In[In>=n ] = n
        I = I[In]
        np.delete(I, -1, 0)
    return I

