import os
import sys
from optparse import OptionParser
sys.path.insert(0, os.path.abspath('./..'))
import vipers

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vipers.settings")
django.setup()
from intellect.Trainer import Trainer

parser = OptionParser()
parser.add_option("-n", '--number', dest="number")
(options, args) = parser.parse_args()

trainer = Trainer(root_path='./..')
trainer.make_training_set(options.number)
