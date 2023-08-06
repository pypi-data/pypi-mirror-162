from __future__ import print_function, unicode_literals

from unicodedata import category

class Utils():

    def __init__(self):

        pass

    def print_version(self):
        version_file = open("version.txt", "r")
        version = version_file.read()
        version_file.close()
        return(version)


    def present_checkbox(self, category_list_for_checkbox, list_type="category"):
        from whaaaaat import Separator, Token, print_json, prompt, style_from_dict

        style = style_from_dict(
            {
                Token.Separator: "#F1C40F",
                Token.QuestionMark: "#FF9D00 bold",
                Token.Selected: "#229954",
                Token.Pointer: "#FF0E0E bold",
                Token.Instruction: "#229954",
                Token.Answer: "#5F819D bold",
                Token.Question: "",
            }
        )


        checkbox_content = [
            {
                'type': 'checkbox',
                'message': 'Select %s' % list_type,
                'name': list_type,
                'choices': category_list_for_checkbox,
                'validate': lambda answer: 'You must choose at least one %s.' % list_type \
                    if len(answer) == 0 else True
            }
        ]

        answers = prompt(checkbox_content , style=style)
        return(answers)
