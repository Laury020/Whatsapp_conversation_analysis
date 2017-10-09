
# TODO comment everything
# TODO create functions that do specific parts
# TODO create a master that calls the functions

# file that you want to use
# be sure to change this before running the script
import glob
allfiles = glob.glob('*.txt')

from Master import Master

for filename in allfiles:
    Master(filename)
