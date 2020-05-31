from ROOT import TTree, TFile, TBrowser, TCanvas, gRandom

##############################################################################
#                                                                            #
#                           Reading data files                               #
#                                                                            #
##############################################################################


#To access the data in a file you need to things, the name of the file, and
#the name of the tree within the file. Assuming you know the file name, the
#name of the tree can be found by opening the file in ROOT and instantiating
#a TBrowser. E.g.

print '''Example of using a TBrowser'''
print '''  * Double click on the file name 'data/example.root' (under ROOT files in the left pane). This will show you the file's contents'''
print '''  * Double click on the tree name 'DataTuple'. This will show you the tree's contents'''
print '''  * Double click on one of the branches 'B_M', 'Kst_M', 'JPsi_M'. This will display a histogram of all the values contained'''


file = TFile('data/example.root')
browser = TBrowser()

raw_input("Press Enter to continue...")


print '''Example of reading a file'''
print '''Opening the tree 'DataTuple' '''
tree = file.Get('DataTuple')

print '''Now we can make some more complicated plots...'''
canvas = TCanvas()

print '''Example 2D plot of B mass vs J/psi mass with a selection on the B mass to lie in the range 5000 < mass < 5500\n\n\n'''

# Here we ask for a 2D plot, with B mass on the x-axis, the J/psi mass on
# the y axis. We place a selection on the B mass to be between 5000 and 4900
# We also ask for the drawing option 'colz' to use a coloured z axis (heat map)
tree.Draw("JPsi_M:B_M", "B_M > 5000 && B_M < 5500", "colz")

raw_input("Press Enter to continue...")



#I'm now going to show you how to access elemenet of the trees
print '''\n\n\nAccessing individual elements'''

for i in xrange(10):
  tree.GetEntry(i)
  print tree.B_M, tree.Kst_M

raw_input("Press Enter to continue...")

#When looping over very large tuples things can be very slow to load. I've
#written a simple wrapper you can use (and examine) to speed things up, and
#it handles opening the file and tree for you
print '''\n\n\nAccessing individual elements with the wrapper'''

from TreeWrapper import TreeWrapper

treewrapper = TreeWrapper('data/example.root', 'DataTuple')

for entry in treewrapper.entry(Nentries=20):
  print treewrapper.B_M, treewrapper.Kst_M

raw_input("Press Enter to continue...")




##############################################################################
#                                                                            #
#                           Writing data files                               #
#                                                                            #
##############################################################################

#I'm going to show you the proper way to do it first, then show you another
#quick wrapper as I did above.

#Writting trees is a little more complicated. We still need a file, let's put
#one in the current directory. We must now specify that we want a writable
#file. The option "recreate" will create a new file ready to write, and will
#overwrite any existing file (be careful)

print '''\n\n\nGoing to write a new tree to the current directory.'''
raw_input("Press Enter to continue...")

out_file = TFile('output.root', 'recreate')

#now we need to make a tree, let's call it myTree
out_tree = TTree('myTree', 'myTree')

#we need a C-style pointer to add a new branch (in python this can be done
#using the array package)

from array import array
mybranch = array('d', [0]) # make it a double precision floating point, and 1 element long

#add a new branch to the tree

out_tree.Branch('myBranch', mybranch, 'myBranch/D') #tell it the name, the address, and the specification (this means a double)

#now we're ready to add the data

mybranch[0] = 1 #set the branch
out_tree.Fill() # This will add the data to all branches that have been created.

#add a few more
mybranch[0] = 2
out_tree.Fill()
mybranch[0] = 3
out_tree.Fill()
mybranch[0] = 4
out_tree.Fill()


#write the data and close the file
out_file.Write()
out_file.Close()

#you should now have some data you can look in the file
canvas2 = TCanvas()
my_tree = TreeWrapper('output.root', 'myTree')
my_tree.Draw('myBranch')


print '''\n\n\nNow going to write another new tree to the current directory using the easy wrapper.'''
raw_input("Press Enter to continue...")

#now the easy wrapper...
from TreeMaker import TreeMaker

#Let's copy all the entries from the original tree, and add some 'weight'
#that we can apply. These could be to correct the distributions for known
#issues, to apply background subtraction, to emulate effects, etc. These
#will be to pretend we have different statistically similar samples by
#applying weights generated from a poisson distribution...

treemaker = TreeMaker(
                      'output2.root',  #output file name
                      'myTree',        #output tree name
                      ['B_M', 'JPsi_M', 'Kst_M', 'Poisson1', 'Poisson2', {'name':'Poisson', 'length':100}]# list of branches, the last one is an array
                     )

for entry in treewrapper.entry():
  treemaker.Fill({ #wants a dictionary of values
                   'B_M': treewrapper.B_M,
                   'JPsi_M': treewrapper.JPsi_M,
                   'Kst_M': treewrapper.Kst_M,
                   'Poisson1': gRandom.PoissonD(1),
                   'Poisson2': gRandom.PoissonD(1),
                   'Poisson':  [gRandom.PoissonD(1) for i in xrange(100)]
                 })
treemaker.close()

canvas3 = TCanvas()
that_tree = TreeWrapper('output2.root', 'myTree')
that_tree.Draw('B_M', 'abs(B_M - 5280) < 50') #Draw the original B mass in a 100 MeV window around the peak
that_tree.Draw('B_M', 'Poisson1*(abs(B_M - 5280) < 50)', 'same hist') #Draw the first poisson fluctuated B mass on the same plot
that_tree.Draw('B_M', 'Poisson2*(abs(B_M - 5280) < 50)', 'same hist') #And the second
that_tree.Draw('B_M', 'Poisson[0]*(abs(B_M - 5280) < 50)', 'same hist') #And some from the array
that_tree.Draw('B_M', 'Poisson[12]*(abs(B_M - 5280) < 50)', 'same hist') #And some from the array

raw_input("Press Enter to Exit...")

