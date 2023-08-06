import numpy as np
import rmsd, math, time, concurrent.futures

###############################################################
####       Written by Fabian Schuhmann                     ####
####       fabian.schuhmann[at].uol.de                     ####
###############################################################


def single_rmsf(A_line,accuracy):
    """
    :param A_line: is a numpy array containing the positions of one selected atom over the whole trajectory
    :param accuracy: a float that allows to set which selected atoms can be discarded
    :return: 1 if the rmsf is lower then the accuracy, else 0

    Description: RMSF stands for Root-Mean-Square Fluctuation. In order to align a protein, sometimes one wishes to 
    only consider residues, which do not move extensively anyhow. Given an accuracy value, gives the binary response, 
    if the residue is within accuracy limits or not.
    """
    sum = 0
    for j in range(len(A_line)):
        sum = +np.linalg.norm(A_line[j] - A_line[0]) ** 2
    div = 1 / len(A_line)
    rmsf = math.sqrt(div * sum)
    if rmsf < accuracy:
        return 1
    else:
        return 0


def parallel_rmsf(A_trans, accuracy, Workers):
    """
    :param A_trans: A numpy array containing the reference atoms to which the protein shall be aligned
    :param accuracy: accuracy for the rmsf discards to be passed on to downstream method single_rmsf()
    :param Workers: the parallelized project can run on multiple Workers. Workers specifies how many CPU should be
    utilized.
    :return: an index list that contains which residues are below the accuracy limit and should be considered
    for the alignment process.

    Description: RMSF stands for Root-Mean-Square Fluctuation. In order to align a protein, sometimes one wishes to only 
    consider residues, which do not move extensively anyhow. Given an accuracy value, gives the binary response, if a 
    single residue is within accuracy limits or not. We then return a sorted list of the calculated binary values.
    """
    with concurrent.futures.ProcessPoolExecutor(max_workers=Workers) as executor:
        results = executor.map(single_rmsf, A_trans,[accuracy]*len(A_trans))

    indexset = []
    results = list(results)
    for i in range(len(results)):
        if results[i] == 1:
            indexset.append(i)
    print(f"Length RMSF List, Accuracy {accuracy}: {len(indexset)}/{len(A_trans)}")
    return indexset


def rmsf(A_trans, accuracy):
    """
    This is a single processor version of parallel_rmsf and is not actively used anymore.

    :param A_trans: A numpy array containing the reference atoms to which the protein shall be aligned
    :param accuracy: accuracy for the rmsf discards to be passed on to downstream method
    :return: an index list that contains which residues are below the accuracy limit and should be considered
    for the alignment process.

    Description: RMSF stands for Root-Mean-Square Fluctuation. In order to align a protein, sometimes one wishes to only 
    consider residues, which do not move extensively anyhow. Given an accuracy value, gives the binary response, if a 
    single residue is within accuracy limits or not. We then return a sorted list of the calculated binary values.
    """
    indexset = []
    for i in range(len(A_trans)):
        sum = 0
        for j in range(len(A_trans[i])):
            sum = sum + (np.linalg.norm(A_trans[i][j] - A_trans[i][0]) ** 2)
        div = 1 / len(A_trans[i])
        rmsf = math.sqrt(div * sum)
        if rmsf < accuracy:
            indexset.append(i)
    return indexset


def get_limited_selection_list(Names, selection):
    """
    :param Names: A names list as returned by Preparation.getList()
    :param selection: a list of atom names e.g. ["CA","N"]
    :return: index list of atoms to be considered for further methods, e.g. DistanceMatrix calculations
    """
    nameIndex = []
    for i in range(len(Names)):
        for item in selection:
            found = False
            if str(Names[i])[-2:].replace("-", "") == item:
                nameIndex.append(True)
                found = True
                break
        if not found:
            nameIndex.append(False)

    sel = []
    for i in range(len(nameIndex)):
        if nameIndex[i]:
            sel.append(i)
    return sel


def get_selection_from_protein(referencepdb, selection):
    """
    This should be used, if the getList numpy array is not further altered since the getList initialization.
    :param referencepdb: The chunk saved by the getList method in the preparation, it is an mdtraj object containing
    the necessary information to allow a vmd like selection in the mdtraj environment
    :param selection: Takes a vmd like expression to choose atoms
    :return: returns index list of atoms to be considered in the e.g. Distance Matrix

    Note: In numerous tests the selection threw an error, if CA was combined with other atoms. This gave rise
    to this somewhat ambigious looking function, in which one can either choose CA or not at all.
    """
    topology = referencepdb.topology
    if "name CA" in selection:
        if selection == "name CA":
            sel = [atom.index for atom in topology.atoms if (atom.name == 'CA')]
        else:
            exit("There is an error with your selection, name CA acts up in combination with other selected fields")
    else:
        sel = topology.select(selection)
    return sel


def get_limited_backbone(Names):
    """
    :param Names: A names list as returned by Preparation.getList()
    :return: index list of atoms to be considered for further methods, here the selection automatically
    only takes the backbone without the oxygen into consideration.
    """
    nameIndex = []
    for i in range(len(Names)):
        if str(Names[i])[-2:].replace("-", "") == "CA" or str(Names[i])[-2:].replace("-", "") == "C" or str(Names[i])[
                                                                                                        -2:].replace(
            "-", "") == "N" or str(Names[i])[-2:].replace("-", "") == "BB":
            nameIndex.append(True)
        else:
            nameIndex.append(False)
    sel = []
    for i in range(len(nameIndex)):
        if nameIndex[i]:
            sel.append(i)
    return sel


def get_limited_selection(Names,selection):
    """
    :param Names: A names list as returned by Preparation.getList()
    :param selection: an indexset of atoms starting from 0.
    :return: index list of atoms to be considered for further methods, this method first reduces everything to the
    backbone atoms, but furthermore then only considers residues whose indices are also in a given index set. This
    allows a selection for alignment, if one does not want to align according to the whole protein.
    """
    nameIndex = []
    for i in range(len(Names)):
        if str(Names[i])[-2:].replace("-", "") == "CA" or str(Names[i])[-2:].replace("-", "") == "C" or str(Names[i])[-2:].replace("-", "") == "N" or str(Names[i])[-2:].replace("-", "") == "BB":
            atom=''.join([s for s in str(Names[i]) if s.isdigit()])
            try:
                if int(atom) in selection:
                    nameIndex.append(True)
            except ValueError:
                pass
        else:
            nameIndex.append(False)
    sel = []
    for i in range(len(nameIndex)):
        if nameIndex[i]:
            sel.append(i)
    return sel

def align_one(A_long, Names,accuracy=0.05, Workers=1,selection=[],RMSD_threshold=0.5):
    """
    :param A_long: An atom list as returned by Preparation.getList()
    :param Names: a list of names as returned by Preparation.getList()
    :param accuracy: (default=0.01 nm) the accuracy level for the RMSF judgement
    :param Workers: (default=1) Number of CPUs used
    :param selection: (default=[]) indexset of selection, default aligns the whole protein
    :param RMSD_threshold: (default 0.01 nm) A threshold set. RMSD has to be smaller than this value finish alignment
    :return: Returns a numpy array in the style of getList that is aligned to itself. The complete alignment scheme
    is:
    1. Generate an indexlist of residues that move less than an accuracy level using RMSF
    2. Align everything to the first frame as a reference
    3. Calculate RMSD and finish if RMSD below 0.01
    4. Align everything to the new average structure
    5. Go to 3.
    """
    print("Begin Align one")
    if selection==[]:
        sel = get_limited_backbone(Names)
    else:
        sel= get_limited_selection(Names, selection)
    A = A_long[:,sel,:]

    start = time.perf_counter()
    A_trans = np.transpose(A, axes=[1, 0, 2])
    indexset = parallel_rmsf(A_trans, accuracy, Workers)
    #A_trans = np.asarray([A_trans[index] for index in indexset])
    A_reduced = A[:,indexset,:]

    A_Av = A[0]
    counter = 0
    List_of_RMSD=[]
    while True:

        counter += 1
        print(f"Alignment step {counter} after {round(time.perf_counter() - start, 2)} seconds.")
        A_reduced_av = A_Av[indexset]# np.asarray([A_Av[i] for i in indexset])
        RMSD = 0
        for i in range(len(A)):
            A_reduced[i]=A_reduced[i]-rmsd.centroid(A_reduced[i])
            A_long[i]=A_long[i]-rmsd.centroid(A_long[i])
            Rotation = rmsd.kabsch(A_reduced[i], A_reduced_av)
            A_reduced[i] = np.dot(A_reduced[i], Rotation)

            A[i] = np.dot(A[i], Rotation)
            A_long[i] = np.dot(A_long[i], Rotation)
            RMSD = RMSD + rmsd.rmsd(A[i], A_Av)

        RMSD = RMSD / len(A)
        List_of_RMSD.append(RMSD)
        if RMSD< RMSD_threshold*10:
            break
        if counter==100:
            break
        for item in List_of_RMSD:
            if item <= RMSD and item>RMSD_threshold:
                print(f"Circular RMSD run, adjusting threshold from {RMSD_threshold} nm to {item/10} nm.")
                RMSD_threshold=item/10
        A_Av = np.mean(A, axis=0)
    return A_long, indexset


def align_relative(A_long, B_long, indexset):
    """This function should not be called by itself and will be called by Align_states

    :param A_long, B_long: coordinate list as returned by Preparation.getList()
    :param indexset: indexset that contains the indices of residues that survived the rmsd check for both
    trajectories that should be aligned relatively.
    :return: in the process B_long is aligned to fit A_long. Only the new and altered B_long is returned.
    """

    print("Begin align relative")
    A_reduce = A_long[:,indexset,:]
    B_reduce=B_long[:,indexset,:]


    for i in range(len(A_long)):
        Rotation = rmsd.kabsch(B_reduce[i], A_reduce[i])
        B_long[i] = np.dot(B_long[i], Rotation)

    return B_long


def Align_states(A, B, ANames, BNames,accuracy=0.01,Workers=1,selection=[[],[]],RMSD_threshold=0.01):
    """
    :param A,B: coordinate lists as returned by Preparation.getList()
    :param ANames, BNames: lists of names as returned by Preparation.getList()
    :param accuracy: (default=0.01 nm) accuracy float to determine the rmsf accuracy in alignment
    :param Workers: (default=1) numbers of allowed cpu for parallelized rmsf
    :param RMSD_threshold: (default 0.01 nm) A threshold set. RMSD has to be smaller than this value finish alignment
    :return: Returns a numpy array in the style of getList that is aligned to itself. The complete alignment scheme
    :param selection: (default=[[],[]]) a list containing two lists, first corresponding to A, and second corresponding
    to B to allow for a certain selection for alignment purposes in each trajectory. The resulting selections need to
    match in number and should be comparable for decent results. The default will choose the whole protein.
    :return: returns two aligned coordinate lists matching the layout of the ones returned by Preparation.getList().

    Description: First the two trajectories are aligned individually according to their individual selection. In a
    second step the shorter length trajectory is aligned to the longer length trajectory and both aligned trajectories
    are returned.
    """

    print(A.shape,B.shape)

    print("Begin align states")
    A, Aindex = align_one(A, ANames, accuracy, Workers, selection[0],RMSD_threshold)
    B, Bindex = align_one(B, BNames, accuracy, Workers, selection[1],RMSD_threshold)
    catIndex = list(set(Aindex) & set(Bindex))
    if len(A) >= len(B):
        A = align_relative(B, A, catIndex)
    else:
        B = align_relative(A, B, catIndex)
    print("Done align states")
    return A, B


if __name__ == "__main__":
    pass
