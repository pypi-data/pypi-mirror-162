from cvascode.core.utils import DataIngestor, Templater, DocxTemplater
from cvascode import __version__


def version(args):
    print(__version__)


def template(args):
    context = DataIngestor.ingest(args.data_file)
    template = DocxTemplater(args) if args.docx else Templater(args)
    template.render(context)
