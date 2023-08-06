import os
import chevron
from ..path import rel_to_abs


class expand_template:
    """
    Example:
        expand_template(
            name='config_gen.py',
            template='./config.template.ts',
            out="../web/apps/chatroom/src/",
            substitutions={
                "xxxkey": "xxxvalue",
            },
        )
    """

    def __init__(self, name: str, out: str, substitutions: dict, template: str):
        self.name = name
        self.out = out
        self.substitutions = substitutions
        self.template = template
        self._gen_code()

    @staticmethod
    def write_targe_path(target_path: str, content: str):
        with open(target_path, 'w') as f:
            f.write(content)

    def _gen_code(self):
        with open(rel_to_abs(self.template, return_str=True), 'r') as f:
            result = chevron.render(f, self.substitutions)
            print(result)
            self.write_targe_path(rel_to_abs(os.path.join(self.out, self.name), return_str=True), result)

