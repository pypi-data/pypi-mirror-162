import mdtraj as md
import numpy as np
import time
import rmsd
from re import sub

def saver(inputList, atomNames, name):
    """
    :param inputList: The numpy array prepared by Preparation.getList()
    :param atomNames: the numpy array of names as prepared by Preparation.getList()
    :param name: The file name to save the resulting arrays
    :return: No return

    Description: This is merely a helper to save the resulting numpy arrays. The helper function exists to
    make sure that everything is saved accordingly, even if an early break occurs.
    """
    np.save(arr=np.asarray(inputList), file=f"{name}", allow_pickle=True)
    np.save(arr=atomNames, file=f"{name}_names", allow_pickle=True)

def remove_unnecessary(chunk, exclude=[], Atomnames=[]):
    """
    :param exclude: A list of unnecessary residue names: see get_List().
    :param Atomnames: A list of unnecessary atom names: see get_List(). 

    Description: Removes water and ions (Na, Cl), as well as any residues and atoms specified by the user.
    """
    #Remove water from selection:
    sel1 = [atom.index for atom in chunk.atoms if not atom.residue.is_water]
    #Remove to be excluded residues:
    sel_exclude= [atom.index for atom in chunk.atoms if not atom.residue in exclude]
    #Remove atoms by name:
    sel=list(set(sel1) & set(sel_exclude))
    Atomnames=Atomnames+["SOD", "CLA","W","CL","NA"]
    for item in Atomnames:
        sel2 = [atom.index for atom in chunk.atoms if not atom.name == item]
        sel=list(set(sel) & set(sel2))

    return sel

def find_exclude_list(chunk):
    """Finds residues, whose resid is already taken by a different residue in the structure and marks the
    additional finds to be excluded by remove_unnecessary()"""
    excludes=[]
    residues=[str(atom) for atom in chunk.atoms if atom.name=="N"]
    indexes=[]
    for item in residues:
        resid=int(sub("[^0-9]","",item))
        if not resid in indexes:
            indexes.append(resid)
        else:
            excludes.append(item[:item.find("-")])

    return excludes

def getList(dcds, psf, name, Stride=1, number=0, skip=0, exclude=[], find_exclude=False, remove_atoms=["SOD","CLA"]):
    """
    :param dcds: A list containing the strings with the paths to the dcd files that want to be prepared
    :param psf: a string that contains the path to the psf file that is the basis for the .dcd files.
    :param name: A name for the trajectory passed to getList. This determines the file name to which the
    resulting numpy arrays will be saved. This is mandatory to ensure the creation of a backup file.
    :param Stride: (default 1) An integer that indicates the step to go through the dcd. Example: A stride of 2 would
    mean, that only every second frame is read in.
    :param number: an integer that allows to set an upper bound for the number of frames
    :param skip: an integer that allows to set the number of frames to be skipped at the beginning
    :param exclude: list of strings that allows the exclusion of residues, syntax of the strings has to be
    e.g. SER29 to exclude Serine at position 29.
    :param find_exclude if one does not know, if there are doubles that need to be removed, find_exclude True will
    attempt a fix, results are to be handled with care
    :param remove_atoms is a list of atom names not specifically connected to a residue which should be removed. Default
    removes standard IONS.
    :return: returns a numpy array containing all the geometric information of each atom in the simulation except
    for water and ions and a numpy array containing the names of all these atoms. Finally, it returns an md.traj object
    containing the information of the very first frame. This allows selection methods, if needed.

    Description: This is the supporting function, that converts a psf and dcds into the needed numpy array.
    dcds is a list of strings containing the file names of the dcds in either relative or absolute paths.
    psf is the psf file associated with the dcds
    Stride defines the step size. This can greatly decrease memory usage.
    number is the maximum number of frames considered and skip allows to skip the first frames completely. This
    is handy, in case one was waiting for a structure to equilibrate.
    In total (number-skip)/Stride frames will be considered.

    FAQ: 
    1. Can I have two different psfs for two different structures with two different dcds?
        Of course, but that would be two structures and so you would run getList() twice, once for each structure
    2. What is a negative selection?
        A negative selection means, you choose the things you want to exclude and you specifically do not choose
        the things you want to keep.
    3. What if there are other salts than NaCl?
        This iteration deals with the standard salt. If additional salts are needed, one can jump to
        remove_unnecessary() and add the salt names to list of atomnames.
        
    """
    start = time.perf_counter()
    frameNumber = 0
    counter = 0
    atomNames = []
    if number ==0:
        for File in dcds:
            for chunk in md.iterload(filename=File, top=psf, skip=0, chunk=1):
                number+=1
                if number %200==0:
                    print(f"Getting Total Frame Count. Counted {number} so far")
    for File in dcds:
        for chunk in md.iterload(filename=File, top=psf, skip=0, chunk=1):
            if frameNumber == 0:
                FirstFrame = chunk
                top = chunk.topology
                if len(exclude)==0 and find_exclude:
                    exclude=find_exclude_list(top)
                sel = remove_unnecessary(top, exclude, remove_atoms)
                n=(number-skip)/Stride
                if not n==int(n):
                    n=int(n+1)
                n=int(n)
                atomNames = [atom for atom in chunk.topology.atoms if atom.index in sel]
                inputList = np.zeros((n, len(sel), 3))
            if frameNumber >= skip and frameNumber % Stride == 0:
                if frameNumber >= number:
                    saver(inputList, atomNames, name)
                    return np.asarray(inputList), atomNames, FirstFrame
                if counter % 100 == 0:
                    print(
                        f"\nStarting on frame {frameNumber} after {format(np.round(time.perf_counter() - start, 2), '.2f')} seconds",
                        end='')
                print(".", end='', flush=True)
                points = np.asarray([chunk.xyz[0][index] for index in sel])
                points -= rmsd.centroid(points)
                points = np.reshape(points, (1,) + points.shape)
                inputList[counter] = points
                counter += 1
            frameNumber = frameNumber + 1
        print()

    if frameNumber<number:
        #TODO: This needs to be tested!
        print("Error, you are asking for more frames then your dcds can provide! Attempting to truncate...")
        remove_index=[]
        for i in range(len(inputList)):
            if np.all(inputList[-i])==0:
                remove_index.append(-i)
        inputList=np.delete(inputList,remove_index)

    saver(inputList, atomNames, name)
    return np.asarray(inputList), atomNames, FirstFrame


if __name__ == "__main__":
    pass
