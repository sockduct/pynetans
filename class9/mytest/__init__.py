# Notes
#
# This causes recursive import
#import mytest.simple

# Import module options
#import world
#from . import world
#from mytest import world
#from .world import func1
#from mytest.world import func1

from mytest.world import func1
from mytest.simple import func2
from mytest.whatever import func3

