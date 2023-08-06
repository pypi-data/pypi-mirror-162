#######################################################################################################################
#######################################################################################################################
# ____/\\\\\\\\\\\__________/\\\\____________/\\\\__/\\\\\\\\\\\\\__________________/\\\\\\_________________          #
# ___/\\\/////////\\\_______\/\\\\\\________/\\\\\\_\/\\\/////////\\\_______________\////\\\_________________         #
#  __\//\\\______\///___/\\\_\/\\\//\\\____/\\\//\\\_\/\\\_______\/\\\__________________\/\\\_________________        #
#   ___\////\\\_________\///__\/\\\\///\\\/\\\/_\/\\\_\/\\\\\\\\\\\\\\______/\\\\\_______\/\\\_____/\\\\\\\\\\_       #
#    ______\////\\\_______/\\\_\/\\\__\///\\\/___\/\\\_\/\\\/////////\\\___/\\\///\\\_____\/\\\____\/\\\//////__      #
#     _________\////\\\___\/\\\_\/\\\____\///_____\/\\\_\/\\\_______\/\\\__/\\\__\//\\\____\/\\\____\/\\\\\\\\\\_     #
#      __/\\\______\//\\\__\/\\\_\/\\\_____________\/\\\_\/\\\_______\/\\\_\//\\\__/\\\_____\/\\\____\////////\\\_    #
#       _\///\\\\\\\\\\\/___\/\\\_\/\\\_____________\/\\\_\/\\\\\\\\\\\\\/___\///\\\\\/____/\\\\\\\\\__/\\\\\\\\\\_   #
#        ___\///////////_____\///__\///______________\///__\/////////////_______\/////_____\/////////__\//////////__  #
#######################################################################################################################
#######################################################################################################################
# Authors                                                                                                             #
# Fabian Schuhmann,  Carl-von-Ossietzky Universität Oldenburg                                                         #
# Leonie Ryvkin,  Technische Universiteit Eindhoven                                                                   #
# James D. McLaren,  Carl-von-Ossietzky Universität Oldenburg                                                         #
# Luca Gerhards,  Carl-von-Ossietzky Universität Oldenburg                                                            #
# Ilia A. Solov'yov,  Carl-von-Ossietzky Universität Oldenburg                                                        #
#                                                                                                                     #
#                                                                                                 #
#                                                                                                                     #
# MIT License                                                                                                         #
#                                                                                                                     #
# Version Date: 2022/06/16                                                                                            #
#######################################################################################################################

import numpy as np
import os
import sys
import time

"""
SiMBols supplies two classes. The Trajectory class takes an array of form (x,y,3) or (y,3), which is considered to be
the ordered sequence of the locations in the trajectory. The second class, the Comparer, takes two objects of the
Trajectory class and does the similarity calculations.
"""

class HiddenPrints:
    """
    Helper Class: Allows to supress print().
    """
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


class Trajectory:
    """
    The trajectory class serves as a way to read and treat trajectories.
    :param array: a numpy array of form (time, objects, 3) or (objects, time, 3) or (time,3) containing the
    trajectory's location data. If no array is given, other parameters are checked, whether an array can be loaded
    from a previously generated numpy save (.npy)
    :param index: Sometimes the array contains more objects than are actually needed/wanted for analysis. Index is
    a list of indices to be considered for analysis.
    :param path: If no array has been given to the argument 'array' when initilizing this path is checked, whether
    it leads to a numpy save (.npy) that can be loaded to be the trajectory
    :param name: A name can be set for the trajectory. Can be very helpful to keep track of multiple trajectories.
    The name is picked up by different instances to inform about the progress and what trajectory is being worked with
    at the moment. As a default, the name will just number the instances of the trajectory class.

    Note: Methods whose name starts with an underscore '_' are not meant to be called directly, but are rather called
    by other methods within the class.
    """
    counter = 0

    def __init__(self, array=np.asarray([]), index=[], path="", name=""):
        Trajectory.counter += 1
        self.name = name
        if self.name == "":
            self.name = f"trajectory_{Trajectory.counter}"

        if len(array) != 0:
            self.array = array
        else:
            try:
                if ".npy" not in path:
                    print("File extension .npy not specified, assuming .npy")
                    path = path + ".npy"
                self.array = np.load(path, allow_pickle=True)
            except FileNotFoundError:
                print("Trajectory numpy save not found. Check path name")
                exit(1)

        if len(self.array.shape)==2:
            shape=self.array.shape
            self.array=np.reshape(self.array,(1,self.array.shape[0],self.array.shape[1]))
            print(f"While loading {self.name}, the object dimension was missing, corrected by "
                  f"adding a dummy object dimension with one object. Trajectory shape has been"
                  f"altered from {shape} to {self.array.shape}")
        elif len(self.array.shape)!=3:
            print(f"The uploaded array has dimensions that are not understood: {self.array.shape}. Sorry.")
            exit(1)

        if len(index) == 0:
            self.index = list(range(self.array.shape[1]))
        else:
            self.index = index

        print(f"Loaded trajectory '{self.name}' with dimensions {self.array.shape}.")

    def save(self, outfile=""):
        """
        :param outfile: Outfile is an optional path to where a trajectory numpy file is supposed to be saved. If 
        left blank, the file will be saved with the name of the trajectory in the current working directory.
        """
        if outfile=="":
            outfile=self.name

        np.save(arr=self.array, file=outfile)

    def otc(self, index=[], frames=0, stride=1,transpose=False):
        """
        The distance measures are designed to accept the trajectory in a form (object, timestep, 3)
        with 3 being coordinates in the 3-dimensional space. This procedure takes trajecotries with the
        form (timestep, object, 3) or (object,timestep,3) and turns it to the correct format to be used later.
        otc can also be used to set the number of timesteps and the Index for the trajectory if not all
        objects are meant to be considered. otc is short for object_timesteps_coords.

        :param index: indexlist to make a selection in A
        :param frames: (default=0) number of frames considered, if frames is zero, all frames are considered.
        :param stride: (default=1) stepsize
        :param transpose: (default=False) If transpose is True, the first and second dimension of the trajectory are
        flipped.
        """
        old_shape = self.array.shape
        if len(index) == 0:
            Index = self.index
        else:
            Index = index

        if transpose:
            axes=[1,0,2]
        else:
            axes=[0,1,2]

        A = self.array
        if not frames == 0:
            A = np.transpose(A[:frames:stride, Index, :], axes=axes)
        else:
            A = np.transpose(A[:self.array.shape[0]:stride, Index, :], axes=axes)

        self.array = A
        print(f"Transformed trajectory '{self.name}' of shape {old_shape} to shape {self.array.shape}.")

    def _split(self, Sequence, Segments, Length, Steps):
        result = np.zeros((Steps + 1, 3))
        result[0] = Sequence[0]
        result[-1] = Sequence[-1]
        step = Length / Steps
        for i in range(1, Steps):
            current = step * i
            for j in range(len(Segments) - 1):
                if Segments[j] < current < Segments[j + 1]:
                    position = (Segments[j + 1] - Segments[j]) / (Segments[j + 1] - current)
                    direction = (Sequence[j + 1] - Sequence[j]) / np.linalg.norm(Sequence[j + 1] - Sequence[j])
                    result[i] = Sequence[j] + position * direction
                    break
        return result

    def _length(self, A):
        Seg = np.zeros(len(A))
        Len = 0
        for i in range(1, len(A)):
            Len += np.linalg.norm(A[i] - A[i - 1])
            Seg[i] = Len
        return Seg, Len

    def _helper_sequencer(self, A_line, Steps):
        seg_A, len_A = self._length(A_line)
        result_A = self._split(A_line, seg_A, len_A, Steps)
        return result_A

    def sequencer(self, Steps=0, Workers=1):
        """
        The sequencer is a tool to alter the length of a trajectory by linearly placing elements along the
        path given by the trajectory. This allows to increase or decrease the number of timestep present while
        somewhat keeping the trajectory intact (the fewer steps, the more deviations)

        :param Steps: The number of timesteps that will be present after the sequencer has been applied.
        :param Workers: Workers for parallelization to employ multiple processes.
        """

        import concurrent.futures
        factor = len(self.array)
        with concurrent.futures.ProcessPoolExecutor(max_workers=Workers) as executor:
            result = executor.map(self._helper_sequencer, self.array, [Steps] * factor)

        self.array=np.asarray(list(result))


class Comparer:
    """
    The Comparer class takes two objects of the trajectory class to then use similarity measures to compare them. All
    measures can be called with an argument timer=True (default = False) to display the run time in seconds upon
    completion.
    Additionally, the class contains helping methods to make sure the two trajectories are viable for comparison
    and results can be saved.
    """
    def __init__(self, Traj1, Traj2):
        if not isinstance(Traj1, Trajectory) and not isinstance(Traj2, Trajectory):
            exit("Trajectory objects needs to be given to the Comparer")
        self.Traj1 = Traj1
        self.Traj2 = Traj2
        self.traj1 = Traj1.array
        self.traj2 = Traj2.array
        self.name = f"{Traj1.name}_vs_{Traj2.name}"
        print(f"Comparer: {self.name}")
        self.measure_names = ["Discrete Frechet Distance", "Discrete Weak Frechet Distance", "Dynamic Time Warping",
                              "Hausdorff Distance", "Longest Common Subsequence", "Difference Distance Matrix",
                              "Wasserstein Distance", "Kullback-Leibler Divergence"]
        self.measure = [True] * 8
        with HiddenPrints():
            self.make_Check()

        # Measures:
        self.DFD = None
        self.DWFD = None
        self.DTW = None
        self.HD = None
        self.LCSS = None
        self.DDM = None
        self.DDM_Matrix = None
        self.WD = None
        self.KLD = None

        #Measure Helpers
        self.dtw_delta=np.inf

    def make_Check(self):
        """
        make_Check does not take any parameters and checks the trajectories supplied for measures that are applicable
        and informs about its result. Furthermore, it will update an "allowed list", so a measure can be stopped
        before investing computation time, if it will not terminate anyway.
        """
        self.measure = [True] * 8
        print(f"Number of objects...", end='')
        if self.traj1.shape[0] == self.traj2.shape[0]:
            print("OK")
            objects = True
        else:
            print("Problematic")
            objects = False
        print("Length of trajectories...", end='')
        if self.traj1.shape[1] == self.traj2.shape[1]:
            print("equal")
            length = True
        else:
            print("Not equal")
            length = False
        print("Dimension...", end='')
        if self.traj1.shape[2] != 3 or self.traj2.shape[2] != 3:
            print("Problematic")
            dimension = False
        else:
            print("OK")
            dimension = True

        if not dimension:
            self.measure = [False] * 8
        if not objects:
            self.measure = [False] * 8
        if not length:
            self.measure[7] = False
            self.measure[6] = False
            self.measure[5] = False

    def which(self):
        """
        which() gives additional output, that tells a user, which similarity measures are allowed for the
        given trajectories.
        """
        with HiddenPrints():
            self.make_Check()
        if True in self.measure:
            print("Allowed measures:")
            for i in range(len(self.measure)):
                if self.measure[i]:
                    print(self.measure_names[i])

        else:
            print("No suitable measure found for the comparison of the two trajectories")

    def cut(self):
        """
        cut adjusts the number of timesteps by simply cutting the end of the longer trajectory. For a more
        sophisticated approach, the sequencer method of each trajectory instance can be called beforehand 
        to adjust the number of timesteps.
        """
        length = min(self.traj1.shape[1], self.traj2.shape[1])

        self.traj1 = self.traj1[:, :length, :]
        self.traj2 = self.traj2[:, :length, :]

        print(f"Trajectories have been cut at the end to a length of {length} elements.")

    def save_all(self,name=""):
        """
        save_all() checks for all already calculated similarity measures and will save the result as a numpy array.
        :param name: If a name is given, a path to save the files can be specified. File endings should be ommited.
        """
        if name=="":
            name=self.name
        save_dict={'DFD':self.DFD,'DWFD':self.DWFD,'DTW':self.DTW,'HD':self.HD,'LCSS':self.LCSS,'DDM':self.DDM,'DDM_Matrix':self.DDM_Matrix,'WD':self.WD,'KLD':self.KLD}
        for key in save_dict:
            if save_dict[key] is not None:
                np.save(arr=save_dict[key],file=f"{name}_{key}")
                print(f"Saved result for {key}.")

    def wd(self, timer=False):
        """
        wd calculated the Wasserstein measure between two trajectory.
        :param timer: (default=False) if timer is set to true, the time it took to complete the calculation
        of the similarity measure is printed.
        """
        with HiddenPrints():
            self.make_Check()
        if not self.measure[6]:
            print("The Wasserstein measure is not suitable for the chosen trajectories")
            exit(1)
        from scipy.stats import wasserstein_distance
        print("Begin Wasserstein:")
        start = time.perf_counter()
        result = np.zeros((len(self.traj1)))
        for i in range(len(self.traj1)):
            summe = 0
            for j in range(3):
                summe += wasserstein_distance(self.traj1[i].T[j], self.traj2[i].T[j])
            result[i] = summe
        if timer:
            print(f"Wasserstein cycle complete after {round(time.perf_counter() - start, 2)} second(s)!")
        else:
            print("Wasserstein completed!")
        self.WD = result

    def _find_translate_for_KL(self, A):
        translate = np.zeros(3)
        for i in range(len(A)):
            for j in range(len(A[i])):
                for k in range(len(A[i][j])):
                    if A[i][j][k] < translate[k]:
                        translate[k] = A[i][j][k]

        return translate

    def _translater(self, A, translate):
        for i in range(len(A)):
            for j in range(len(A[i])):
                A[i][j] -= translate
                A[i][j] += np.ones(3)

        return A

    def kld(self, timer=False, symmetric=True):
        """
        kld calculated the Kullback-Leiber divergence for two trajectories.

        :param timer: (default=False) if timer is set to true, the time it took to complete the calculation
        of the similarity measure is printed.
        :param symmetric: (default=True) In general the kld measure is not symmetric, which is corrected by
        considering the mean of the two directed versions. This is called the Jenssen-Shannon divergence and considered
        by default. If symmetric is set to False, the kld from traj1 to traj2 is calculated.

        Note: KL divergence only allows possible values (logarithm is used). In order to apply this to a 3d
        trajectory in which negative values in the single coordinate values are allowed, a translation is employed.
        The whole trajectory is proportionally moved to the subset of R^3 in which x>0,y>0 and z>0. The KL divergence
        is taken from scipy.stats.
        """
        with HiddenPrints():
            self.make_Check()
        if not self.measure[7]:
            print("The Kullback-Leibler measure is not suitable for the chosen trajectories")
            exit(1)
        from scipy.stats import entropy

        print("Begin KL Divergence:")
        start = time.perf_counter()

        translate_A = self._find_translate_for_KL(self.traj1)
        translate_B = self._find_translate_for_KL(self.traj2)

        translate = np.zeros(3)
        for i in range(len(translate)):
            translate[i] = min(translate_A[i], translate_B[i])

        A = self._translater(self.traj1, translate)
        B = self._translater(self.traj2, translate)

        print(A.shape, B.shape)
        result = np.zeros(A.shape[0])
        for i in range(len(result)):
            summe = 0
            for j in range(A.shape[1]):
                if symmetric:
                    summe += (entropy(pk=A[i][j], qk=B[i][j]) + entropy(pk=B[i][j], qk=A[i][j])) / 2
                else:
                    summe += entropy(pk=A[i][j], qk=B[i][j])
            result[i] = summe

        if timer:
            print(f"Kullback-Leibler cycle complete after {round(time.perf_counter() - start, 2)} second(s)!")
        else:
            print("Kullback-Leibler completed")
        self.KLD = result

    def _get_Matrix(self, A):
        print("Beginn get_Matrix")
        Matrices = np.zeros((len(A[0]), len(A[0])))
        for k in range(len(A)):
            for i in range(len(A[k])):
                for j in range(len(A[k])):
                    Matrices[i][j] += np.linalg.norm(A[k][i] - A[k][j])

        return Matrices

    def ddm(self, timer=False, Workers=1):
        """
        ddm calculates the difference distance measure measure between two trajectory.
        :param timer: (default=False) if timer is set to true, the time it took to complete the calculation
        of the similarity measure is printed.
        :param Workers: (default=1) Number of processes used for calculation


        Note: The measure is close to useless, if the number of objects is one, e.g. A has shape (1,timesteps,3).
        This measure was shown to be useful for the comparison of protein simulation trajectories.
        """
        with HiddenPrints():
            self.make_Check()
        if not self.measure[5]:
            print("The Difference Distance measure is not suitable for the chosen trajectories")
            exit(1)

        print("Begin Distance Matrix Calculation (parallel)")
        start = time.perf_counter()
        A = np.transpose(self.traj1, axes=[1, 0, 2])
        B = np.transpose(self.traj1, axes=[1, 0, 2])
        split_time = len(A) // Workers
        length = len(A)

        parallel_A = np.reshape(A[:split_time * Workers], (Workers, split_time, A.shape[1], A.shape[2]))
        parallel_B = np.reshape(B[:split_time * Workers], (Workers, split_time, B.shape[1], B.shape[2]))

        import concurrent.futures
        with concurrent.futures.ProcessPoolExecutor(max_workers=Workers) as executor:
            print("Preparation of first Matrix:")
            results_A = executor.map(self._get_Matrix, parallel_A)
            print("Preparation of second Matrix:")
            results_B = executor.map(self._get_Matrix, parallel_B)

        results_A = np.asarray(list(results_A))
        results_B = np.asarray(list(results_B))
        results_A = np.sum(results_A, axis=0)
        results_B = np.sum(results_B, axis=0)
        results_A_2 = np.zeros((len(A[0]), len(A[0])))
        results_B_2 = np.zeros((len(A[0]), len(A[0])))
        if split_time * Workers != length:
            non_parallel_A = A[split_time * Workers:]
            non_parallel_B = B[split_time * Workers:]

            results_A_2 = self._get_Matrix(non_parallel_A)
            results_B_2 = self._get_Matrix(non_parallel_B)

        results_A = results_A + results_A_2
        results_B = results_B + results_B_2

        results_A /= length
        results_B /= length
        Outputmatrix = np.abs(np.subtract(results_A, results_B))
        if timer:
            print(f"Difference Distance Matrix cycle complete after {round(time.perf_counter() - start, 2)} second(s)!")
        else:
            print("Difference Distance Matrix completed")
        self.DDM_Matrix = Outputmatrix
        self.DDM = np.mean(self.DDM_Matrix, axis=0)

    def _lcss_calc(self, M, delta):
        dist_mat = np.zeros(np.asarray(M.shape) + 1)
        for i in range(M.shape[0]):
            for j in range(max(0, i - delta), min(M.shape[1], i + delta)):
                if M[i, j] == 1:
                    dist_mat[i + 1, j + 1] = dist_mat[i, j] + 1
                else:
                    dist_mat[i + 1, j + 1] = max(dist_mat[i, j + 1], dist_mat[i + 1, j])

        return dist_mat[-1, -1]

    def _lcss_matrix(self, A, B, epsilon, delta):
        Matrix = np.zeros((A.shape[0], B.shape[0]))
        for i in range(len(Matrix)):
            for j in range(len(Matrix[i])):
                if np.linalg.norm(A[i] - B[j]) < epsilon:
                    Matrix[i][j] = 1
        returnee = 1 - (self._lcss_calc(Matrix, delta) / min(A.shape[0], B.shape[0]))
        return returnee

    def lcss(self, epsilon, delta=np.inf, timer=False, Workers=1):
        """
        This method calculates the longest common subsequence regarding an epsilon and respective a delta bound for
        the number of objects in the arrays A and B. The process is parallelized and for each object the binarized
        distance matrix according to epsilon is calculated. This Matrix is then given to the real lcss method.

        :param epsilon: The threshold to classify, which two values are similar. Two points are considered similiar,
        if their distance is lower than epsilon
        :param delta: Mainly used to increase runtime. Delta reduces the considered steps by denying access to points
        that are too far apart in terms of their position in the sequence.
        :param Workers: (default=1) Number of CPU allowed for this process
        :param timer: (default=False) if timer is set to true, the time it took to complete the calculation
        of the similarity measure is printed.
        """
        start = time.perf_counter()
        import concurrent.futures
        with concurrent.futures.ProcessPoolExecutor(max_workers=Workers) as executor:
            results = executor.map(self._lcss_matrix, self.traj1, self.traj2, [epsilon] * len(self.traj1),
                                   [delta] * len(self.traj1))

        if timer:
            print(f"Longest Common Subsequence cycle complete after {round(time.perf_counter() - start, 2)} second(s)!")
        else:
            print("Longest Common Subsequence completed")
        self.LCSS = list(results)

    def hd(self, timer=False):
        """
        hd calculates the hausdorff measure between two trajectory.
        :param timer: (default=False) if timer is set to true, the time it took to complete the calculation
        of the similarity measure is printed.
        """
        from scipy.spatial.distance import directed_hausdorff
        print("Begin Hausdorff:")
        start = time.perf_counter()
        result = np.zeros((len(self.traj1)))
        for i in range(len(self.traj1)):
            helper1, _, _ = directed_hausdorff(u=self.traj1[i], v=self.traj2[i], seed=None)
            helper2, _, _ = directed_hausdorff(u=self.traj2[i], v=self.traj1[i], seed=None)
            result[i] = max(helper1, helper2)
        if timer:
            print(f"Hausdorff cycle complete after {round(time.perf_counter() - start, 2)} second(s)!")
        else:
            print("Hausdorff completed")
        self.HD = result

    def _single_dtw(self, A, B):
        if 'dtaidistance' not in sys.modules:
            from dtaidistance import dtw_ndim

        sum = dtw_ndim.distance(A, B,window=self.dtw_delta)
        return sum

    def dtw(self, delta=np.inf,timer=False, Workers=1):
        """
        dtw calculates the dynamic time warping measure between two trajectory.
        :param timer: (default=False) if timer is set to true, the time it took to complete the calculation
        of the similarity measure is printed.
        :param delta: (default=infinity) maximum window size to reduce time difference
        :param Workers: Number of CPU allowed for this operation.
        """
        print("Begin DTW:")
        start = time.perf_counter()
        A = np.asarray(self.traj1, dtype=np.double)
        B = np.asarray(self.traj2, dtype=np.double)
        self.dtw_delta=delta

        import concurrent.futures
        with concurrent.futures.ProcessPoolExecutor(max_workers=Workers) as executor:
            result = executor.map(self._single_dtw, A, B)

        if timer:
            print(f"Dynamic time warping cycle complete after {round(time.perf_counter() - start, 2)} second(s)!")
        else:
            print("Dynamic time warping completed")
        self.DTW = list(result)

    def _path_finder(self, M, epsilon):
        """
        :param M: A distance Matrix as produced in weak_frechet_single() and passed down through the methods
        :param epsilon: epsilon is a float taken from the array of possibles in path_in_matrix. It is used to
        binary search the distance matrix and create a graph based on this adjacency matrix. If a path in this
        graph exists, epsilon is a possible solution for the weak FrÃ©chet measure

        :return: returns the boolean value 'True', if a path exists from the top left of the adjacency matrix
        to the bottom right. And 'False', if not
        """

        # test edge cases
        if M[0, 0] > epsilon or M[-1, -1] > epsilon:
            return False

        li = len(M)
        lj = len(M[0])

        # we want to remember for a position i,j if we can reach it starting at 0,0
        reachable = np.full([li + 1, lj + 1], False)
        reachable[0, 0] = True
        # the matrix reachable is larger than it needs by one
        # this makes it way easier to access the 8 cells around a cell without checking if a cell
        # is on the border of the matrix
        # these two loops ensure that we won't access those cells
        for i in range(li + 1):
            reachable[i, lj] = True
        for j in range(lj + 1):
            reachable[li, j] = True

        found_end = False
        stack = [(0, 0)]  # this is a list, so appending and removing elements at the end only take small constant time.

        while len(stack) > 0 and not found_end:
            (i, j) = stack.pop()  # we take the last element and look at its neighbors
            for di in [i - 1, i, i + 1]:
                for dj in [j - 1, j, j + 1]:
                    if not reachable[di, dj] and M[di, dj] <= epsilon:
                        if di == li - 1 and dj == lj - 1:
                            found_end = True
                            return found_end
                        # we managed to reach this particular cell for the first time, so we label it and put it in
                        # the stack to look at it (and its neighbors) later
                        reachable[di, dj] = True
                        stack.append((di, dj))

        return found_end

    def _path_in_matrix(self, Matrix, possibles):
        """
        :param Matrix: the distance matrix, where in entry i,j, we have the distance between the points object1[i]
        to object2[j]
        :param possibles: a sorted list of distances from the matrix M that can still be solutions
        :return: returns the actual weak Fréchet distance from the distance matrix.
        """

        result = possibles[-1]
        if len(possibles) == 1:
            return result

        median_index = (len(possibles) - 1) // 2
        median = possibles[median_index]

        if self._path_finder(Matrix, median):
            result = self._path_in_matrix(Matrix, possibles[:median_index + 1])
        else:
            result = self._path_in_matrix(Matrix, possibles[median_index + 1:])
        return result

    def _weak_frechet_single(self, a, b):
        """
        :param a,b: Two numpy arrays of shape (objects,3) to calculate the weak fréchet distance for this
        certain pair of objects.
        :return: returns a number that gives the weak fréchet distance between the trajectories for object a and b
        """
        Matrix = np.zeros((len(a), len(b)))
        for i in range(len(Matrix)):
            for j in range(len(Matrix[i])):
                Matrix[i][j] = np.linalg.norm(a[i] - b[j])
        possibles = np.sort(Matrix.flatten())
        result = self._path_in_matrix(Matrix, possibles)
        return result

    def dwfd(self, timer=False, Workers=1):
        """
        dwfd calculates the discrete weak frechet distance between two trajectories
        :param timer: (default=False) if timer is set to true, the time it took to complete the calculation
        of the similarity measure is printed.
        :param Workers: Number of CPU allowed for this operation.
        """
        print("Begin Weak Frechet Parallel:")
        start = time.perf_counter()
        import concurrent.futures
        with concurrent.futures.ProcessPoolExecutor(max_workers=Workers) as executor:
            result = list(executor.map(self._weak_frechet_single, self.traj1, self.traj2))

        if timer:
            print(f"Discrete weak Frechet distance cycle complete"
                  f"after {round(time.perf_counter() - start, 2)} second(s)!")
        else:
            print("Discrete weak Frechet distance completed")
        self.DWFD=np.asarray(result)

    def _frechet_dist(self, object1, object2):
        """
        :params object1,object2: two trajectories to calculate their Fréchet distance
        -> are this objects the ones from odt above?
        :return: float number containing the Fréchet distance between object1 and object2 trajectories.
        """
        n = len(object1)
        m = len(object2)
        ca = np.full(m, -1.)

        # put the Fŕechet distance between object1[0] and object2[0->j] into the array ca
        norm = np.linalg.norm(object1[0] - object2, axis=-1)  # Note: dist(a, b) = norm(a - b)

        ca[0] = norm[0]
        for j in range(1, m):
            ca[j] = max(ca[j - 1], norm[j])

        # put the Fŕechet distance between object1[0->i] and object2[0->j] into the array ca
        for i in range(1, n):
            norm = np.linalg.norm(object1[i] - object2, axis=-1)

            diagonal = ca[0]
            ca[0] = max(ca[0], norm[0])
            for j in range(1, m):
                new_val = max(norm[j], min(ca[j], diagonal, ca[j - 1]))
                diagonal = ca[j]
                ca[j] = new_val

        return ca[m - 1]

    def dfd(self, timer=False, Workers=1):
        """
        dfd calculates the discrete frechet distance between two trajectories.
        :param timer: (default=False) if timer is set to true, the time it took to complete the calculation
        of the similarity measure is printed.
        :param Workers: Number of CPU allowed for this operation.
        """
        start = time.perf_counter()
        print("Begin parallel Frechet")
        import concurrent.futures
        with concurrent.futures.ProcessPoolExecutor(max_workers=Workers) as executor:
            results = executor.map(self._frechet_dist, self.traj1, self.traj2)

        if timer:
            print(f"Discrete Frechet distance cycle complete after {round(time.perf_counter() - start, 2)} second(s)!")
        else:
            print("Discrete Frechet distance completed")
        self.DFD=list(results)


if __name__ == "__main__":
    pass
