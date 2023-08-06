# Data autocorrelation spectral similarity
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import re
import h5py
import csv
from charset_normalizer import from_bytes
from pylab import figure, cm
from matplotlib.colors import LogNorm
from matplotlib.gridspec import GridSpec
from itertools import combinations
from scipy.spatial.distance import euclidean
from scipy.signal import resample, decimate
from scipy import sparse
from scipy.sparse.linalg import spsolve
from numpy.linalg import norm
from tqdm import tqdm

class autocorrelate:
    def __init__(self):
        print('Local version')
        pass
        
    @staticmethod
    def natural_sort(l): 
        '''
        Sort a list of strings in a human friendly way.

        Parameters
        ----------
        l : list
            List of strings to be sorted.
        '''
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(l, key=alphanum_key)

    @staticmethod
    def parse_filename(filename):
        '''
        Parse a file name to get the sample name.
        Overwrite for specific data if you want to use the dataframe directly

        Parameters
        ----------
        filename : str
            File name to be parsed.
        '''
    # return str(int(filename.split('.')[-2].split('_')[-1]))
        return filename.split('-')[1].split('_')[0]

    def read_folder(self, root, filetype):
        '''
        Read all files in a folder.
        Specify the filetype (e.g. h5, csv).
        
        Parameters
        ----------
        root : str
            Path to the folder.

        filetype : str
            File type to be read.
        '''
        self.root = root
        self.runname = os.path.normpath(self.root).split(os.path.sep)[-1]
        self.filetype = filetype
        self.files = self.natural_sort(glob.glob(self.root + '/*' + self.filetype))

    def read_data(self, parse_names=False):
        '''
        Read data from a list of files found by read_folder.
        Takes the first column of the first file as the x-values.
        Filetype is specified in read_folder.

        Parameters
        ----------
        parse_names : bool
            If True, parse file names for column headings
        '''
        try:
            maxfiles = len(self.files)


            # Initialize dataframe with x column
            self.df = pd.DataFrame()
            if self.filetype in ['h5', 'hdf5']:
                f = h5py.File(self.files[0])
                def get_data(f):
                    return h5py.File(f)['I'][0]
                self.df['x'] = f['2th']


            elif self.filetype in ['csv', 'txt', 'xy', 'xye', 'tsv']:
                # Find csv delimiter
                sniffer = csv.Sniffer()
                with open(self.files[0], 'r') as sniff_file:
                    delimiter = sniffer.sniff(sniff_file.read(1024)).delimiter

                def get_data(f):
                    return pd.read_csv(f, sep=delimiter, usecols=[0,1], names=['x', 'y'])

                f = get_data(self.files[0])
                self.df['x'] = f['x']

            # Initialise the other columns
            _ = []
            for i in range(maxfiles):

                # HDF type data formats
                if self.filetype in ['h5', 'hdf5']:
                    try:
                        # self.df[split_filename(self.files[i])] = h5py.File(self.files[i])['I'][0]
                        if parse_names:
                            _.append(pd.DataFrame(get_data(self.files[i]), columns=[self.parse_filename(self.files[i])]))
                        else:
                            _.append(pd.DataFrame(get_data(self.files[i]), columns=[self.files[i]]))
                    except:
                        print(f"File {i} is missing data")
                        _.append(pd.DataFrame(np.zeros(self.df.shape[0])+0.1, columns=[self.files[i]]))

                # Delimited data formats
                if self.filetype in ['csv', 'txt', 'xy', 'xye', 'tsv']:
                    try:
                        if parse_names:
                            temp = get_data(self.files[i])
                            temp.rename(columns={'y': self.parse_filename(self.files[i])}, inplace=True)
                            _.append(temp[self.parse_filename(self.files[i])])
                        else:
                            temp = get_data(self.files[i])
                            temp.rename(columns={'y': self.files[i]}, inplace=True)
                            _.append(temp[self.files[i]])
                    except:
                        print(f"File {i} is missing data")
                        _.append(pd.DataFrame(np.zeros(self.df.shape[0])+0.1, columns=[self.files[i]]))

            # Concatenate all dataframes
            self.df = pd.concat([self.df] + _, axis=1)
            
        except:
            print('Error reading data, no data read')

    def read_data_csv(self, path):
        '''
        Read data from a single csv file

        Parameters
        ----------
        path : str
            Path to the csv file
        '''
        self.df = pd.read_csv(path)
        self.df.rename({self.df.columns[0]: 'x'}, axis=1, inplace=True)
        # Fix this
        self.runname = None

    def read_echem_mpt(self, path, decimal=','):
        '''
        Read cycling data from an echem mpt file

        Parameters
        ----------
        path : str
            Path to the mpt file
        '''
        # Speed up encoding detection
        with open(path, 'rb') as f:
            encoding = from_bytes(f.read(2048)).best().encoding

        skip = self.get_skip(path, encoding=encoding)

        _ = pd.read_csv(path, encoding=encoding, sep='\t', decimal=decimal, skiprows=skip)
        _ = resample(_['Ewe/V'], self.df.shape[1]-1)
        self.df_echem = pd.DataFrame(_).T


        
    @staticmethod
    def baseline_arPLS(y, ratio=1e-6, lam=100, niter=10, full_output=False):
        '''
        Baseline correction routine
        '''
        L = len(y)
        diag = np.ones(L - 2)
        D = sparse.spdiags([diag, -2*diag, diag], [0, -1, -2], L, L - 2)
        H = lam * D.dot(D.T)  # The transposes are flipped w.r.t the Algorithm on pg. 252
        w = np.ones(L)
        W = sparse.spdiags(w, 0, L, L)
        crit = 1
        count = 0
        while crit > ratio:
            z = spsolve(W + H, W * y)
            d = y - z
            dn = d[d < 0]
            m = np.mean(dn)
            s = np.std(dn)
            w_new = 1 / (1 + np.exp(2 * (d - (2*s - m))/s))
            crit = norm(w_new - w) / norm(w)
            w = w_new
            W.setdiag(w)  # Do not create a new matrix, just update diagonal values
            count += 1
            if count > niter:
                # print('Maximum number of iterations exceeded')
                break

        if full_output:
            info = {'num_iter': count, 'stop_criterion': crit}
            return z, d, info
        else:
            return z

    @staticmethod
    def bkg_subtract(df):
        '''
        Apply baseline correction to a dataframe

        Parameters
        ----------
        df : pandas.DataFrame
            Dataframe to be corrected
        '''
        # Define cutoffs if necessary
        start, end = None, None

        # Concatenating a list is better than inserting one by one
        _ = []
        for i in tqdm(df.columns[1:]):
            subtracted = df[i][start:end] - autocorrelate.baseline_arPLS(df[i][start:end])
            _.append(subtracted)
        return pd.concat([df['x']] + _, axis=1)

    @staticmethod
    def get_skip(file, encoding='utf-8'):
        '''
        Get the number of rows to skip in a mpt file

        Parameters
        ----------
        file : str
            Path to the mpt file
        encoding : str
            Encoding of the mpt file
        '''
        skip = -1
        with open(file, 'r', encoding=encoding) as f:
            for line in f:
                if 'mode' in line:
                    return skip
                else:
                    skip += 1
        return skip
            
    def autocorrelate(self, samples=None, bkg_subtract=False):
        '''
        Apply autocorrelation to self.df to generate correlation matrix

        Parameters
        ----------
        samples : int
            Number of samples to use for downsampling

        bkg_subtract : bool
            Whether to apply baseline correction first
        '''

        if bkg_subtract:
            self.df = self.bkg_subtract(self.df)
            
        try:
            pairs = list(combinations(self.df.columns[1:], 2))
            array_size = self.df.shape[1]-1
            self.correlation_matrix = np.zeros((array_size, array_size))
            for i in tqdm(pairs):
                if samples:
                    distance = np.corrcoef(
                        resample(self.df[i[0]], samples),
                        resample(self.df[i[1]], samples))[0,1]
                else:
                    distance = np.corrcoef(self.df[i[0]], self.df[i[1]])[0,1]
                self.correlation_matrix[self.df.columns.get_loc(i[0])-1, self.df.columns.get_loc(i[1])-1] = distance
                self.correlation_matrix[self.df.columns.get_loc(i[1])-1, self.df.columns.get_loc(i[0])-1] = distance
            
            # Set the diagonal to one for color consistency
            self.correlation_matrix[np.diag_indices_from(self.correlation_matrix)] = 1

            # Raise baseline to zero
            self.correlation_matrix[self.correlation_matrix < 0] = 0.01
        except:
            print('Could not generate correlation matrix')

    def distance_matrix(self):
        '''
        Generate a distance matrix from a single dimensional array, e.g. e-chem data

        TODO: add in data file reading

        '''
        try:
            pairs = list(combinations(self.df_echem.columns[:], 2))
            array_size = self.df_echem.shape[1]
            self.distance_matrix = np.zeros((array_size, array_size))
            for i in tqdm(pairs):
                distance = np.linalg.norm(self.df_echem[i[0]] - self.df_echem[i[1]])
                self.distance_matrix[self.df_echem.columns.get_loc(i[0])-1, self.df_echem.columns.get_loc(i[1])-1] = distance
                self.distance_matrix[self.df_echem.columns.get_loc(i[1])-1, self.df_echem.columns.get_loc(i[0])-1] = distance
            
            # # Set the diagonal to one for color consistency
            # self.distance_matrix[np.diag_indices_from(self.distance_matrix)] = 1

            # # Raise baseline to zero
            # self.distance_matrix[self.distance_matrix < 0] = 0.01
        except:
            print('Could not generate distance matrix')
       

    def plot(self, vmin=0.995, vmax=1.000):
        plt.imshow(self.correlation_matrix, origin='lower', norm=LogNorm(vmin=vmin, vmax=vmax))
        plt.colorbar()
        plt.show()

    def plot_full(self):
        if self.correlation_matrix is not None:

            vmin = np.quantile(np.reshape(self.correlation_matrix, -1), 0.15)
            vmax = np.quantile(np.reshape(self.correlation_matrix, -1), 0.9)

            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10,10), constrained_layout=True)
            ax2.imshow(self.correlation_matrix, cmap='viridis', origin='lower', norm=LogNorm(vmin=0.995, vmax=1))
            # fig.colorbar(ax.imshow(results_np_resamp, cmap='viridis', origin='lower'))
            start = 1000
            end = 3000
            aspect = len(self.df.columns[1:])/(end - start)

            vmin, vmax = f.df.min().min(), f.df.max().max()

            vmin = self.df[self.df.columns[1]].quantile(0.015)
            vmax = self.df[self.df.columns[1]].quantile(0.9)



            ax1.imshow(self.df.iloc[start:end, 1:].T,
                    # extent = [0, df_bkg_sub.shape[1], df_bkg_sub['x'][0], df_bkg_sub['x'][df_bkg_sub.index[-1]]],
                    norm=LogNorm(vmin=vmin, vmax=vmax), origin='lower')
            # ax2.set_aspect(len(self.df_bkg_sub.columns[1:])/len(self.df_bkg_sub.index))
            ax1.set_aspect(1/aspect)
            ax4.imshow(self.df.iloc[start:end, 1:],
                    # extent = [0, df_bkg_sub.shape[1], df_bkg_sub['x'][0], df_bkg_sub['x'][df_bkg_sub.index[-1]]],
                    norm=LogNorm(vmin=vmin, vmax=vmax))
            # ax2.set_aspect(len(self.df_bkg_sub.columns[1:])/len(self.df_bkg_sub.index))
            ax4.set_aspect(aspect)
            ax3.axis('off')
            
            # How best to get the title?
            # fig.suptitle(self.root.split('/')[-2])
            fig.suptitle(self.root)

            if not os.path.exists('plots'):
                os.makedirs('plots')
            fig.savefig(r'./plots/' + self.root, transparent=False, facecolor='white')
        
            plt.close(fig)
        else:
            print('No data to plot!')

    def plot_full_gs(self, qmin=0.15, qmax=0.9, echem=False):
        '''
        Plot the full correlation matrix and the components

        Parameters
        ----------
        qmin : float
            Minimum quantile to use for the color scale
        qmax : float
            Maximum quantile to use for the color scale
        '''
        if self.correlation_matrix is not None:

            vmin = np.quantile(np.reshape(self.correlation_matrix, -1), qmin)
            vmax = np.quantile(np.reshape(self.correlation_matrix, -1), qmax)

            fig = plt.figure(figsize=(10,12), tight_layout=True)
            gs = GridSpec(6, 7, hspace=0.0, wspace=0.0,
            width_ratios=[1, 1, 1, 1, 1, 0.2, 0.2], height_ratios=[1, 1, 1, 1, 1, 1])

            # fig, ((ax_x, ax2), (ax3, ax_y)) = plt.subplots(2, 2, figsize=(10,10), constrained_layout=True)
            ax_main = fig.add_subplot(gs[1:4, 0:4])
            ax_y = fig.add_subplot(gs[1:4, 4])
            ax_x = fig.add_subplot(gs[0, 0:4])
            ax_cbar = fig.add_subplot(gs[1:4, 6])
            ax_ec = fig.add_subplot(gs[4, 0:4])

            main = ax_main.imshow(self.correlation_matrix, norm=LogNorm(vmin=vmin, vmax=vmax), cmap='viridis', origin='lower', aspect='auto')
            
            plt.colorbar(main, cax=ax_cbar)
            # fig.colorbar(ax_main.imshow(self.correlation_matrix, cmap='viridis', origin='lower'))

            if echem:
                ax_main.contour(self.distance_matrix, origin='lower', cmap='seismic_r')
                ax_ec.plot(self.df_echem.T)
                ax_ec.set_ylabel('V')
                ax_ec.set_xlim(0, len(self.df_echem.columns))

            start = 0
            end = self.df.shape[0] - 1
            # aspect = len(self.df.columns[1:])/(end - start)

            vmin = self.df[self.df.columns[1]].quantile(qmin)
            vmax = self.df[self.df.columns[1]].quantile(qmax)

            ax_y.imshow(self.df.iloc[start:end, 1:].T,
                    extent = [self.df[self.df.columns[0]][start], self.df[self.df.columns[0]][end], 0, self.df.shape[1]],
                    norm=LogNorm(vmin=vmin, vmax=vmax), origin='lower', aspect='auto')

            ax_x.imshow(self.df.iloc[start:end, 1:],
                    extent = [0, self.df.shape[1], self.df[self.df.columns[0]][start], self.df[self.df.columns[0]][end]],
                    norm=LogNorm(vmin=vmin, vmax=vmax), aspect='auto')

            # Set ticks and labels
            ax_main.set_xlabel('Pattern number')
            ax_main.set_ylabel('Pattern number')
            ax_x.set_xticks([])
            ax_x.set_ylabel('x')
            ax_y.set_yticks([])
            ax_y.set_xlabel('x')

            if self.runname:
                fig.suptitle(self.runname)

            if not os.path.exists('plots'):
                os.makedirs('plots')
            fig.savefig(r'./plots/' + self.runname, transparent=False, facecolor='white')

            plt.show()
        
            plt.close(fig)
        else:
            print('No data to plot!')