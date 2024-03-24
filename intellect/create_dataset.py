import os
import sys
from optparse import OptionParser


sys.path.insert(0, os.path.abspath('./..'))
import vipers

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vipers.settings")
django.setup()
from intellect.Trainer import Trainer
from intellect.models import CrawlSession

parser = OptionParser()
parser.add_option("-n", '--number', dest="number")
(options, args) = parser.parse_args()

trainer = Trainer(root_path='./..')
session = CrawlSession.objects.get(pk=options.number)
if session is None:
    trainer.make_training_set(options.number)
else:
    trainer.remake_training_set(options.number)
