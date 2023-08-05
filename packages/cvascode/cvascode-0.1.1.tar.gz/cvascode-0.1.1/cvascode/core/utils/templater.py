from jinja2 import Template
from docxtpl import DocxTemplate


class Templater():
    def __init__(self, args):
        self._template = self._create_template(args)
        self._output = args.output_file

    def _create_template(self, args):
        with open(args.template_file, "r") as file:
            return Template(
                file.read(),
                block_start_string=args.block_start,
                block_end_string=args.block_end,
                variable_start_string=args.variable_start,
                variable_end_string=args.variable_end,
                comment_start_string=args.comment_start,
                comment_end_string=args.comment_end
            )

    def render(self, context):
        filled = self._template.render(context)
        with open(self._output, 'w') as file:
            file.write(filled)


class DocxTemplater(Templater):
    def __init__(self, args):
        super().__init__(args)

    def _create_template(self, args):
        return DocxTemplate(args.template_file)

    def render(self, context):
        self._template.render(context)
        self._template.save(self._output)
